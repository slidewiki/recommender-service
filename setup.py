from setuptools import setup, find_packages

setup(
    name='recommender service',
    version='Beta',
    description='Recommender service using a RESTful API based on Flask-RESTPlus',
    url='',
    author='Jaume Jordán',

    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],

    keywords='rest restful api flask swagger openapi flask-restplus',

    packages=find_packages(),

    install_requires=['flask-restplus', 'Flask-SQLAlchemy', 'numpy', 'scipy', 'requests', 'sklearn'],
)
