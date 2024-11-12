import requests
import sys
import logging
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] - %(message)s')

from concurrent.futures import ThreadPoolExecutor, as_completed

DEPENDENCIES_URL = {
    'python': 'https://pypi.org/project/{package_name}/',
    'js': 'https://registry.npmjs.org/{package_name}/'
}

# Read URLs from standard input and strip whitespace
urls = [line.strip() for line in sys.stdin if line.strip()]

def get_random_user_agent():
    # you can also import SoftwareEngine, HardwareType, SoftwareType, Popularity from random_user_agent.params
    # you can also set number of user agents required by providing `limit` as parameter

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    # Get Random User Agent String.
    user_agent = user_agent_rotator.get_random_user_agent()
    
    return user_agent

def is_unclaimed(package_name: str, language: str) -> tuple[bool,int]:
    """Check if a package name is unclaimed on npm."""
    ua = get_random_user_agent()
    
    logger.debug(f"Checking if package {package_name} exists on npmjs...")
    dependencies_url = DEPENDENCIES_URL[language]
    r = requests.head(dependencies_url.format(package_name=package_name), headers={"User-Agent":ua})
        
    logger.debug(f"status code of package {package_name} is {r.status_code}")
    return r.status_code != 200 and r.status_code != 302, r.status_code  # Returns True if status is not 200 (unclaimed)

def get_dependencies(url: str) -> tuple[list, str]:
    """Fetch dependencies from a package.json URL."""
    logger.debug(f"Checking {url} for dependencies...")
    r = requests.get(url, verify=False, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"})
    all_dependencies = []
    if url.find('package.json') >= 0:
        response_json = r.json()
        dependencies = response_json.get('dependencies', {})
        dev_dependencies = response_json.get('devDependencies', {})
        all_dependencies.extend(dependencies.keys())
        all_dependencies.extend(dev_dependencies.keys())
        language = 'js'
    else:
        response = r.text
        all_dependencies.extend(response.split('\n'))
        language = 'python'
        
    return all_dependencies, language

def check_url_dependencies(url: str):
    """Check all dependencies for a given URL."""
    vulnerabilities = []
    dependencies, language = get_dependencies(url=url)
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(is_unclaimed, dependency, language): dependency for dependency in dependencies}
        for future in as_completed(futures):
            dependency = futures[future]
            try:
                vulnerable, status_code = future.result()
                if vulnerable:  # True if the dependency is unclaimed
                    vulnerabilities.append({"package_name":dependency,"status_code":status_code,"language": language})
            except Exception as e:
                logger.error(f"Error checking dependency {dependency}: {e}")
    return url, vulnerabilities

def main():
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(check_url_dependencies, url): url for url in urls}
        for future in as_completed(futures):
            url, vulnerabilities = future.result()
            for dependency in vulnerabilities:
                logger.info(f"[VULN] {url} [{dependency['package_name']}|{dependency['status_code']}|{dependency['language']}]")
        
if __name__ == "__main__":
    main()
