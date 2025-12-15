# runtests.py (Final Robust Version)

import os
import sys
from django.conf import settings
from django.test.utils import get_runner

# Define your package name here
PACKAGE_NAME = 'lightweight_ratelimit_django'

def run_tests():
    # 1. Add current directory to path (to find the 'settings.py' file)
    sys.path.insert(0, os.path.abspath('src'))

    # 2. Set the settings module environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings') 

    # 3. Configure settings explicitly
    # This ensures settings are loaded immediately, avoiding the ImproperlyConfigured error.
    if not settings.configured:
        settings.configure()
        
    # CRITICAL: Since settings were just loaded, we must now import django
    # and initialize the App Registry.
    import django
    django.setup()
    
    # 4. Run the tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run tests specifically on your package
    failures = test_runner.run_tests([PACKAGE_NAME]) 

    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests()