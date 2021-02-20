import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='interlin-q',
    version='0.0.1.post5',
    scripts=[],
    author="Rhea Parekh, Stephen DiAdamo",
    author_email="stephen.diadamo@gmail.com",
    description="A Distributed Quantum Computing Framework",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Interlin-q/Interlin-q",
    download_url="https://github.com/Interlin-q/Interlin-q/releases/tag/0.0.1",
    keywords=['quantum', 'distributed', 'simulator', 'computing', 'Interlin-q'],
    install_requires=[
        'qunetsim'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
)
