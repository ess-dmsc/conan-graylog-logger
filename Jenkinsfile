def centos = docker.image('essdmscdm/centos-build-node:0.7.2')

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

    try {
        def container_name = "${env.JOB_BASE_NAME}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
        container = centos.run("\
            --name ${container_name} \
            --tty \
            --env http_proxy=${env.http_proxy} \
            --env https_proxy=${env.https_proxy} \
        ")

        stage('Info') {
            sh """docker exec ${container_name} sh -c \"
                cmake3 --version
                conan --version
                cppcheck --version
                git --version
            \""""
        }

        stage('Checkout') {
            sh """docker exec ${container_name} sh -c \"
                git clone https://github.com/ess-dmsc/${env.JOB_BASE_NAME}.git \
                    --branch ${env.BRANCH_NAME}
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
            release_flag = get_release_flag(is_release)
            sh """docker exec ${container_name} sh -c \"
                make_conan_package.sh -k -d ${env.JOB_BASE_NAME}_pkg \
                    ${env.JOB_BASE_NAME} \
                    ${conan_pkg_version} \
                    ${conan_pkg_commit}
            \""""
        }

        stage('Upload') {
            sh """docker exec ${container_name} sh -c \"
                export http_proxy=''
                export https_proxy=''
                upload_conan_package.sh ${env.JOB_BASE_NAME}_pkg/conanfile.py \
                    ${conan_remote} \
                    ${conan_user} \
                    ${conan_pkg_channel}
            \""""
        }
    } finally {
        container.stop()
    }
}
