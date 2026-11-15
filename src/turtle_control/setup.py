from setuptools import setup

setup(
    name='turtle_control',
    version='0.0.1',
    packages=['turtle_control'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/turtle_control']),
        ('share/turtle_control', ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yanchen',
    maintainer_email='yanchen@example.com',
    description='Turtle controller and keyboard teleop',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'controller = turtle_control.controller:main',
        'teleop = turtle_control.teleop:main',
    ]},
)
