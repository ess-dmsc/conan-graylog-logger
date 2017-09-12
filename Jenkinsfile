def project = "graylog-logger"
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

def run_in_container(container_name, script) {
    sh "docker exec ${container_name} sh -c \"${script}\""
}

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
            run_in_container(container_name, """
                cmake3 --version
                conan --version
                cppcheck --version
                git --version
            """)
        }

        stage('Checkout') {
            run_in_container(container_name, """
                git clone https://github.com/ess-dmsc/${project}.git \
                    --branch ${env.BRANCH_NAME}
            """)
        }

        stage('Setup') {
                withCredentials([string(
                    credentialsId: 'local-conan-server-password',
                    variable: 'CONAN_PASSWORD'
                )])
            {
                def setup_script = """
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
                """
                sh "docker exec ${container_name} sh -c \"${setup_script}\""
            }
        }

        stage('Package') {
            release_flag = get_release_flag(is_release)
            def package_script = """
                make_conan_package.sh \
                    ${release_flag} \
                    ${project} \
                    ${pkg_version} \
                    ${pkg_commit}
            """
            sh "docker exec ${container_name} sh -c \"${package_script}\""
        }

        stage('Upload') {
            def upload_script = """
                export http_proxy=''
                export https_proxy=''
                cd ${project}
                ./upload_package.py \
                    ${conan_remote} \
                    ${conan_user} \
                    ${conan_pkg_channel}
            """
            sh "docker exec ${container_name} sh -c \"${upload_script}\""
        }
    } finally {
        container.stop()
    }
}
