def project = "conan-graylog-logger"
def centos = docker.image('essdmscdm/centos-build-node:0.7.0')

def conan_remote = "ess-dmsc-local"
def conan_user = "ess-dmsc"
def conan_pkg_channel = "testing"

properties([
    parameters([
        string(defaultValue: '', description: '', name: 'pkg_version'),
        string(defaultValue: '', description: '', name: 'pkg_commit'),
        booleanParam(defaultValue: false, description: '', name: 'is_release')
    ]),
    pipelineTriggers([])
])

def get_release_flag(is_release) {
    if(is_release) {
        return '-r'
    } else {
        return ''
    }
}

node('docker') {
    try {
        def container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
        container = centos.run("\
            --name ${container_name} \
            --tty \
            --env http_proxy=${env.http_proxy} \
            --env https_proxy=${env.https_proxy} \
        ")

        stage('Info') {
            sh """docker exec ${container_name} sh -c "
                cmake3 --version
                conan --version
                cppcheck --version
                git --version
            " """
        }

        stage('Checkout') {
            sh """docker exec ${container_name} sh -c "
                git clone https://github.com/ess-dmsc/${project}.git \
                    --branch ${env.BRANCH_NAME}
            " """
        }

        stage('Setup') {
                withCredentials([string(
                    credentialsId: 'local-conan-server-password',
                    variable: 'CONAN_PASSWORD'
                )])
            {
                sh """docker exec ${container_name} sh -c "
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
                " """
            }
        }

        stage('Package') {
            release_flag = get_release_flag(is_release)
            sh """docker exec ${container_name} sh -c "
                make_conan_package.sh ${release_flag} \
                    ${project} \
                    ${pkg_version} \
                    ${pkg_commit}
            " """
        }

        stage('Upload') {
            sh """docker exec ${container_name} sh -c "
                export http_proxy=''
                export https_proxy=''
                cd ${project}
                ./upload_package.py \
                    ${conan_remote} \
                    ${pkg_version} \
                    ${conan_user} \
                    ${conan_pkg_channel}
            " """
        }
    } finally {
        container.stop()
    }
}
