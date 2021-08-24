# conan-graylog-logger

Conan package for graylog-logger (https://github.com/ess-dmsc/graylog-logger).

## Updating the conan package

If you have made changes to the *graylog-logger* library and subsequently also want to update the conan-package, follow these instructions:

1. Edit line 7 of the *conanfile.py*-file to set the version of the new conan package. This version should be the same as the the one indicated by the *graylog-logger* tag.

2. Edit line 15 of the *conanfile.py*-file in this repository to checkout the tag or commit of *graylog-logger* that you want to package.

3. When in the directory of the local copy of *conan-graylog-logger*, execute this command:

	```
	conan create .
	```
	Where **x.y.z-dm1** is the same version string as set on line 7 in the *conanfile.py*-file.

4. Upload the new package to the relevant conan package repository by executing:

	```
	conan upload graylog-logger/x.y.z-dm1 --remote alias_of_repository
	```

	Where **x.y.z-dm1** is the version of the conan package as mentioned above and **alias\_of\_repository** is exactly what it says. You can list all the repositories that your local conan installation is aware of by running: `conan remote list`.
