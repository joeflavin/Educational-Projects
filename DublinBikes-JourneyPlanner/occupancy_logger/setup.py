from setuptools import setup, find_packages

with open('requirements.txt') as f: 
    requirements = f.readlines() 
  
long_description = "Log JCDeaux data for dublin bike occupancy."
  
setup( 
        name ='dubbikeslogger', 
        version ='1.0.4', 
        author ='Brian Ryan', 
        author_email ='brian.ryan@ucdconnect.ie', 
        url ='https://github.com/BrianRyan94/dublinbikeslogger.git', 
        description ='Dublin bikes occupancy logger.', 
        long_description = long_description, 
        long_description_content_type ="text/markdown", 
        license ='MIT', 
        packages = find_packages(), 
        entry_points ={ 
            'console_scripts': [ 
                'startdubbikelogger = dublinbikeslogger.dublinbikeslogger:main'
            ] 
        }, 
        keywords ='dublin bikes logger', 
        install_requires = requirements, 
        zip_safe = False
) 
