from setuptools import setup

setup(
    name='parameter_py',
    version='0.0.1',
    packages=['parameter_py'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/parameter_py']),
        ('share/parameter_py', ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yanchen',
    maintainer_email='yanchen@example.com',
    description='ROS 2 parameter exercise in Python',
    license='Apache-2.0',
    entry_points={'console_scripts': ['parameter_node = parameter_py.parameter_node:main']},
)
