@Library('OpenSlateProd')_  // https://github.com/openslate/jenkins-shared-library

def customPublishTask = {
    sh "compose-flow -e ${env.DEPLOY_ENV} --project-name ${env.REPO_NAME} task publish"
}

def publishWhen = { env.TAG_NAME }

openslatePipeline {
    mentions = '@roberto <@marcusian>'
    deployEnv = 'prod'
    lint = true
    lintFunction = customLintFunction
    test = true
    testFunction = customTestFunction
    publish = publishWhen
    publishFunction = customPublishTask
    deploy = false
}
