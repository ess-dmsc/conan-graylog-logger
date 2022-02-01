@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder

project = "conan-graylog-logger"

conan_user = "ess-dmsc"
conan_pkg_channel = "stable"

container_build_bodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian10'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu2004')
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

  builders['macOS'] = get_macos_pipeline()

  try {
    parallel builders
  } catch (e) {
    package_builder.handleFailureMessages()
    throw e
  }

  // Delete workspace when build is done.
  cleanWs()
}

def get_macos_pipeline() {
  return {
    node('macos') {
      cleanWs()
      dir("${project}") {
        stage("macOS: Checkout") {
          checkout scm
        }  // stage

        stage("macOS: Package") {
          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings graylog-logger:build_type=Release \
            --build=outdated"
        }  // stage
      }  // dir
    }  // node
  }  // return
}  // def
