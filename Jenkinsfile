project = "conan-graylog-logger"

def centos = docker.image('essdmscdm/centos-build-node:0.7.3')

def conan_remote = "ess-dmsc-local"
def conan_user = "ess-dmsc"
def conan_pkg_channel = "testing"
def conan_pkg_version = "master"

node('docker') {
    stage('Get Commit') {
        step([
            $class: 'CopyArtifact',
            filter: 'GIT_COMMIT',
            fingerprintArtifacts: true,
            projectName: 'ess-dmsc/graylog-logger/master',
            target: 'artifacts'
        ])
        conan_pkg_commit = sh script: 'cat artifacts/GIT_COMMIT',
            returnStdout: true
    }

    // Delete workspace when build is done
    cleanWs()

    dir("${project}") {
        stage('Checkout') {
            scm_vars = checkout scm
        }
    }

    try {
        def container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
        container = centos.run("\
            --name ${container_name} \
            --tty \
            --env http_proxy=${env.http_proxy} \
            --env https_proxy=${env.https_proxy} \
        ")

        // Copy sources to container.
        sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"

        stage('Info') {
            sh """docker exec ${container_name} sh -c \"
                cmake3 --version
                conan --version
                cppcheck --version
                git --version
            \""""
        }

        stage('Setup') {
                withCredentials([string(
                    credentialsId: 'local-conan-server-password',
                    variable: 'CONAN_PASSWORD'
                )])
            {
                sh """docker exec ${container_name} sh -c \"
                    set +x
                    export http_proxy=''
                    export https_proxy=''
                    conan remote add \
                        --insert 0 \
                        ${conan_remote} ${local_conan_server}
                    conan user \
                        --password '${CONAN_PASSWORD}' \
                        --remote ${conan_remote} \
                        ${conan_user} \
                        > /dev/null
                \""""
            }
        }

        stage('Package') {
            sh """docker exec ${container_name} sh -c \"
                make_conan_package.sh -k -d ${project}_pkg \
                    ${project} \
                    ${conan_pkg_version} \
                    ${conan_pkg_commit}
            \""""
        }

        stage('Upload') {
            sh """docker exec ${container_name} sh -c \"
                export http_proxy=''
                export https_proxy=''
                upload_conan_package.sh -f PACKAGE_NAME \
                    ${project}_pkg/conanfile.py \
                    ${conan_remote} \
                    ${conan_user} \
                    ${conan_pkg_channel}
            \""""
        }

        stage('Archive') {
            sh """docker exec ${container_name} sh -c \"
                tar czvf ${project}_pkg.tar.gz ${project}_pkg
            \""""

            // Remove files outside container.
            sh "rm -f PACKAGE_NAME ${project}_pkg.tar.gz"
            // Copy files from container.
            sh "docker cp ${container_name}:/home/jenkins/PACKAGE_NAME ."
            sh "docker cp ${container_name}:/home/jenkins/${project}_pkg.tar.gz ."

            archiveArtifacts "PACKAGE_NAME,${project}_pkg.tar.gz"
        }
    } finally {
        container.stop()
    }
}
