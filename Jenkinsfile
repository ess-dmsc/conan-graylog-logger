project = "conan-graylog-logger"

conan_remote = "ess-dmsc-local"
conan_user = "ess-dmsc"
conan_pkg_channel = "testing"
conan_pkg_version = "master"

images = [
    'centos': [
        'name': 'essdmscdm/centos-build-node:0.7.6',
        'sh': 'sh'
    ],
    'centos-gcc6': [
        'name': 'essdmscdm/centos-gcc6-build-node:0.1.3',
        'sh': '/usr/bin/scl enable rh-python35 devtoolset-6 -- /bin/bash'
    ]
]

base_container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def get_pipeline(image_key) {
    return {
        def container_name = "${base_container_name}-${image_key}"
        try {
            def image = docker.image(images[image_key]['name'])
            def custom_sh = images[image_key]['sh']
            def container = image.run("\
                --name ${container_name} \
                --tty \
                --network=host \
                --env http_proxy=${env.http_proxy} \
                --env https_proxy=${env.https_proxy} \
                --env local_conan_server=${env.local_conan_server} \
            ")

            // Copy sources to container and change owner and group.
            sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"
            sh """docker exec --user root ${container_name} ${custom_sh} -c \"
                chown -R jenkins.jenkins /home/jenkins/${project}
            \""""

            stage("${image_key}: Conan setup") {
                    withCredentials([string(
                        credentialsId: 'local-conan-server-password',
                        variable: 'CONAN_PASSWORD'
                    )])
                {
                    sh """docker exec ${container_name} ${custom_sh} -c \"
                        set +x
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

            stage("${image_key}: Package") {
                sh """docker exec ${container_name} ${custom_sh} -c \"
                    make_conan_package.sh -k -d ${project}_pkg \
                        ${project} \
                        ${conan_pkg_version} \
                        ${conan_pkg_commit}
                \""""
            }

            stage("${image_key}: Upload") {
                sh """docker exec ${container_name} ${custom_sh} -c \"
                    upload_conan_package.sh ${project}/conanfile.py \
                        ${conan_remote} \
                        ${conan_user} \
                        ${conan_pkg_channel}
                \""""
            }



            stage("${image_key}: Archive") {
                sh """docker exec ${container_name} sh -c \"
                    tar czvf ${project}-${image_key}_pkg.tar.gz ${project}_pkg
                \""""

                // Copy files from container.
                sh "docker cp ${container_name}:/home/jenkins/PACKAGE_NAME ./PACKAGE_NAME-${image_key}"
                sh "docker cp ${container_name}:/home/jenkins/${project}_pkg.tar.gz ./{project}_pkg-${image_key}.tar.gz"

                archiveArtifacts "PACKAGE_NAME-${image_key},${project}_pkg-${image_key}.tar.gz"
            }
        } finally {
            sh "docker stop ${container_name}"
            sh "docker rm -f ${container_name}"
        }
    }
}

node('docker') {
    def builders = [:]

    // Delete workspace when build is done
    cleanWs()

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

    dir("${project}") {
        stage('Checkout') {
            scm_vars = checkout scm
        }
    }

    for (x in images.keySet()) {
        def image_key = x
        builders[image_key] = get_pipeline(image_key)
    }
    parallel builders

    // Archive CentOS artefacts with old name for compatibility
    sh "cp PACKAGE_NAME-centos PACKAGE_NAME"
    sh "cp ${project}_pkg-centos.tar.gz ${project}_pkg.tar.gz"
    archiveArtifacts "PACKAGE_NAME,${project}_pkg.tar.gz"
}
