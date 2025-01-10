@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder

project = "conan-graylog-logger"

conan_user = "ess-dmsc"
conan_pkg_channel = "stable"

container_build_bodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc11'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian11'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu2204')
]

package_builder = new ConanPackageBuilder(this, container_build_bodes, conan_pkg_channel)
package_builder.activateEmailFailureNotifications()
package_builder.defineRemoteUploadNode('centos')

builders = package_builder.createPackageBuilders { container ->
  package_builder.addConfiguration(container, [
    'settings': [
      'graylog_logger:build_type': 'Release'
    ]
  ])
}

node {
  checkout scm
  
  try {
    parallel builders
  } catch (e) {
    package_builder.handleFailureMessages()
    throw e
  }

  // Delete workspace when build is done.
  cleanWs()
}
