import os
import sys
from django.conf import settings
from django.test.utils import get_runner


PACKAGE_NAME = 'lightweight_ratelimit_django'

def run_tests():
    sys.path.insert(0, os.path.abspath('src'))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings') 

    if not settings.configured:
        settings.configure()

    import django
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests([PACKAGE_NAME]) 

    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests()