from setuptools import setup, find_packages

with open('requirements.txt') as f: 
    requirements = f.readlines() 
  
long_description = "Log OpenWeatherMap.org data for Dublin,IE."
  
setup( 
        name ='openweathermaplogger',
        version ='1.0.7',
        author ='OffTheChain',
        author_email ='joseph.flavin@ucdconnect.ie',
        url ='https://github.com/joeflavin/OffTheChain',
        description ='OpenWeatherMap.org Dublin Weather Logger.',
        long_description = long_description, 
        long_description_content_type ="text/markdown", 
        license ='MIT', 
        packages = find_packages(), 
        entry_points ={ 
            'console_scripts': [ 
                'startweatherlogger = openweathermaplogger.openweathermaplogger:main'
            ] 
        }, 
        keywords ='openweathermap weather logger',
        install_requires = requirements, 
        zip_safe = False
) 
