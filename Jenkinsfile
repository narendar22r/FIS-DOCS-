#! /usr/bin/env groovy

@Library(['incubator-lib','cm-cicd-pipeline-library@multikube-azure']) _
//@Library(['cm-cicd-pipeline-library@multikube-azure']) _

String ParamFile = 'params.yaml', branchName, buildno, deployment, stagelog, mavenlog, testlog, ArtifactUrl,
       ArtifactoryURL, BlackDuckUrl, BlackDuckProjectName, BlackDuckProjectVersion, BlackDuckCreds, BlackDuckDetectUrl,
       VeracodeAppName, VeracodeCreds, VeracodeSandbox, ProxyHost, ProxyPort, emailid , checkmarxurl, checkmarxcred , scanregion, projectname , projectgroup, projecttags
Boolean isCheckout, isBuild, isVeracode, isBlackduck, isSonar,isCheckmarx, isCxone , isDeployDev, isDeployQC

def excludeList="package.json"
properties([disableConcurrentBuilds(), buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')),
			parameters([
						booleanParam(defaultValue: true, name: 'Checkout'),
						booleanParam(defaultValue: true, name: 'Build'),
						booleanParam(defaultValue: true, name: 'Blackduck'),
						booleanParam(defaultValue: true, name: 'Veracode'),
						booleanParam(defaultValue: true, name: 'Sonar'),
                        booleanParam(defaultValue: true, name: 'Checkmarx'),
              			 [
                            $class: 'ChoiceParameter', 
                            choiceType: 'PT_SINGLE_SELECT', 
                            description: '''<br>Select scan type as 'dev' for development Scan  <br>Select scan type as 'prod' for CGR report / Final Scan 
< br > Select scan type as 'feature' for playground scan (test scan)''',
                            filterLength: 1, 
                            filterable: false, 
                            name: 'scan_type', 
                            randomName: 'choice-parameter-1688737509871600',
                            referencedParameters: 'Checkmarx', 
                            script: 
                            [
                                $class: 'GroovyScript', 
                                fallbackScript: [
                                    classpath: [], 
                                    sandbox: true, 
                                    script: ''
                                    ], 
                                    script: [
                                    classpath: [], 
                                    sandbox: true, 
                                    script: 'return[\'feature\',\'dev\',\'prod\']']
                            ]
                            ],
                        booleanParam(defaultValue: true, name: 'Cxone'),
						booleanParam(defaultValue: true, name: 'DeployDev'),
                        booleanParam(defaultValue: true, name: 'DeployQC')
           
]
)
])

node('jdk8') {
    stage("Read Parameters") {
        cleanWs()
        checkout scm
        def datas = readYaml file: "./${ParamFile}"
        branchName = "${env.BRANCH_NAME}"
        jobname = "${env.JOB_NAME}"
        buildno = "${env.BUILD_NUMBER}"
        deployment = datas.vars.deployment
        ArtifactoryURL = datas.vars.ArtifactoryURL
        SonarQubeCreds = datas.sonar.credentials
        isCheckout = datas.stages.checkout
        isBuild = datas.stages.build
        isBlackduck = datas.stages.blackduck
        isVeracode = datas.stages.veracode
        isSonar = datas.stages.sonar
        isCheckmarx = datas.stages.checkmarx
        isCxone = datas.stages.cxone
        checkmarxcred = datas.checkmarx.checkmarxcred
        checkmarxurl = datas.checkmarx.checkmarxurl
        cxoneprojectname = datas.cxone.projectname
        cxoneprojectgroup = datas.cxone.projectgroup
        cxoneprojecttags = datas.cxone.projecttags
        isDeployDev = datas.stages.deploy_dev
        isDeployQC = datas.stages.deploy_qc
        emailid = datas.vars.emailid
        if (params.Checkout || params.Build || params.Blackduck || params.Veracode || params.Sonar 
            || params.Checkmarx || params.Cxone || params.DeployDev || params.DeployQC)
        {
            isCheckout = params.Checkout
            isBuild = params.Build
            isBlackduck = params.Blackduck
            isVeracode = params.Veracode
            isSonar = params.Sonar
            isCheckmarx = params.Checkmarx
            isCxone = params.Cxone
            isDeployDev = params.DeployDev
            isDeployQC = params.DeployQC
        }
        else {
            isCheckout = datas.stages.checkout
            isBuild = datas.stages.build
            isBlackduck = datas.stages.blackduck
            isVeracode = datas.stages.veracode
            isSonar = datas.stages.sonar
            isCheckmarx = data.stages.checkmarx
            isCxone = data.stages.cxone
            isDeployDev = datas.stages.deploy_dev
            isDeployQC = datas.stages.deploy_qc
        }
    }
}

def label = "${env.BUILD_NUMBER}".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '_') + "_label"
def snapshotLocation = "ds-maven-snapshot-local/com/fisglobal/"
def releaseLocation = "ds-maven-release-local/com/fisglobal/"
def revision
def version
def cloudId = 'ds-cicd'
def namespace = 'ds-cicd'
def workingdir = "/home/jenkins"
def mavenImg = "ds-docker-dev.docker.fis.dev/maven:3.6-jdk-8"
def images = [
    jnlp: "ds-docker-dev.docker.fis.dev/base-images/base-jenkins-client:1.0.4",
    node: "ds-docker-dev.docker.fis.dev/node:20.18.2", nodeCpuLmt: "3", nodeMemLmt: "4Gi",
    maven: "ds-docker-dev.docker.fis.dev/maven:3.6-jdk-8", mavenCpuLmt: "1", mavenMemLmt: "4Gi"
]
def stages = [:]

milestone()
try {
    if (isBuild || isBlackduck || isSonar || isVeracode || isSonar || isCheckmarx || isCxone) {
        timestamps {
            slaveTemplate = new PodTemplates(cloudId, namespace, label, images, workingdir, this)
            echo "Container images: ${images}"
            echo "running agents on node with label ${label}"
            slaveTemplate.BuilderTemplate {
                node(slaveTemplate.podlabel) {
                    if (isCheckout) {
                        stage("Checkout") {
                            try {
                                cleanWs()
                                checkout scm
                                version = (readMavenPom().version).split('-')[0]
                                revision = "-" + new Date().format("yyyyMMdd.HHmmss-SSS", TimeZone.getTimeZone('UTC'))
                            }
                            catch (e) {
                                currentBuild.result = "ABORTED"
                                def latestcommitHash = sh(script: "git rev-parse origin/${branchName}", returnStdout: true).trim()
                                println "Latest commit hash: ${latestcommitHash}"
                                error('!!!! Git commit hash code differs cannot continue with build !!!!')
                            }
                        }
                    }
                    if (isBuild) {
                        stage ("Source Build")
                        {
                            container('node') {
                                sh """mkdir -p ${WORKSPACE}/deployment"""
                                sh "rm -rf /home/jenkins/.cache/"
                                sh "mkdir -p /home/jenkins/.cache/cypress"
                                withEnv(["http_proxy=http://10.7.199.135:8080/", "https_proxy=http://10.7.199.135:8080/", "NO_PROXY=fisdev.local", "CYPRESS_CACHE_FOLDER=/home/jenkins/.cache/cypress/"]) {
                                    //withEnv(["CYPRESS_CACHE_FOLDER=/home/jenkins/.cache/cypress/"]){
                                    if (readMavenPom().version.contains("SNAPSHOT"))
                                    {
                                        deployment = "SNAPSHOT"
                                        dir("qfscorecompareui")
                                        {
                                            sh """node -v && npm -v"""
                                            sh """rm -f package-lock.json """
                                            sh """node -v && npm -v && npm install && npm run build"""
                                          	sh """ echo "workspace - ${WORKSPACE}, Version -${version}, Revision - ${revision}" """
                                            sh """cd ${WORKSPACE}/dist/apps/qfscorecompareui && tar -cf ${WORKSPACE}/deployment/qfscorecompareui-${version}${revision}-qa.tar *"""
                                            sh """rm -rf ${WORKSPACE}/qualifilescorecompare/dist/apps/qfscorecompareui/"""
                                            sh """ echo "${ArtifactoryURL}/${snapshotLocation}qualifile/qfscorecompareui/${version}-${deployment}/qfscorecompareui-${version}${revision}-qa.tar" >> ${WORKSPACE}/deployment/Artifacts-qfscorecompareui-${version}-${deployment}.ini  """
                                        }
                                      
                                      
                                        dir("deployment")
                                        {
                                            deploymentLocation = snapshotLocation + "qualifile/qfscorecompareui" + "/" + version + "-" + deployment
                                            rtServer (id: 'Artifactory-1', url: "${ArtifactoryURL}", credentialsId: 'f70c497a-59ed-4ad9-ac37-86bb4a31bd4a', bypassProxy: true, timeout: 300)
                                            rtUpload (
                                                serverId: 'Artifactory-1',
                                                spec: '''{
                                                      "files": [
                                                                  {
                                                                      "pattern": "**.tar",
                                                                      "target": "''' 
                                                    + deploymentLocation + '''/"
                                                                  },
                                                                  {
                                                                      "pattern": "**.ini",
                                                                      "target": "''' 
                                                    + deploymentLocation + '''/"
                                                                  }
                                                              ]
                                              }'''
                                            )
                                        }
                                    }
                                    else {
                                        revision = ""
                                        deployment = "RELEASE"
                                        dir("qfscorecompareui") {
                                            sh """node -v && npm -v"""
                                            sh """npm cache clean --force"""
                                            sh """rm -f package-lock.json """
                                            sh """npm install && npm run build:qc"""
                                            sh """cd ${WORKSPACE}/dist/apps/qfscorecompareui && tar -cf ${WORKSPACE}/deployment/qfscorecompareui-${version}${revision}-qa.tar *"""
                                            sh """rm -rf ${WORKSPACE}/qualifilescorecompare/dist/apps/qfscorecompareui/"""
                                            sh """ echo "${ArtifactoryURL}/${releaseLocation}qualifile/qfscorecompareui/${version}/qfscorecompareui-${version}${revision}-qa.tar" >> ${WORKSPACE}/deployment/Artifacts-${version}.ini  """
                                            sh """node -v && npm -v && npm install && npm run build:uat"""
                                            sh """cd ${WORKSPACE}/dist/apps/qfscorecompareui && tar -cf ${WORKSPACE}/deployment/qfscorecompareui-${version}${revision}-uat.tar *"""
                                            sh """rm -rf ${WORKSPACE}/qualifilescorecompare/dist/apps/qfscorecompareui/"""
                                            sh """ echo "${ArtifactoryURL}/${releaseLocation}qualifile/qfscorecompareui/${version}/qfscorecompareui-${version}${revision}-uat.tar" >> ${WORKSPACE}/deployment/Artifacts-${version}.ini  """
                                            sh """node -v && npm -v && npm install && npm run build:perf"""
                                            sh """cd ${WORKSPACE}/dist/apps/qfscorecompareui && tar -cf ${WORKSPACE}/deployment/qfscorecompareui-${version}${revision}-perf.tar *"""
                                            sh """rm -rf ${WORKSPACE}/qualifilescorecompare/dist/apps/qfscorecompareui/"""
                                            sh """ echo "${ArtifactoryURL}/${releaseLocation}qualifile/qfscorecompareui/${version}/qfscorecompareui-${version}${revision}-perf.tar" >> ${WORKSPACE}/deployment/Artifacts-${version}.ini  """
                                            sh """node -v && npm -v && npm install && npm run build:prod"""
                                            sh """cd ${WORKSPACE}/dist/apps/qfscorecompareui && tar -cf ${WORKSPACE}/deployment/qfscorecompareui-${version}${revision}-prod.tar *"""
                                            sh """rm -rf ${WORKSPACE}/qualifilescorecompare/dist/apps/qfscorecompareui/"""
                                            sh """ echo "${ArtifactoryURL}/${releaseLocation}qualifile/qfscorecompareui/${version}/qfscorecompareui-${version}${revision}-prod.tar" >> ${WORKSPACE}/deployment/Artifacts-${version}.ini  """
                                        }
                                        dir("deployment")
                                        {
                                            deploymentLocation = releaseLocation + "qualifile/qfscorecompareui" + "/" + version
                                            rtServer (id: 'Artifactory-1', url: "${ArtifactoryURL}", credentialsId: 'f70c497a-59ed-4ad9-ac37-86bb4a31bd4a', bypassProxy: true, timeout: 300)
                                            rtUpload (
                                                serverId: 'Artifactory-1',
                                                spec: '''{
                                                    "files": [
                                                                  {
                                                                      "pattern": "**.tar",
                                                                      "target": "''' 
                                                    + deploymentLocation + '''/"
                                                                  },
                                                                  {
                                                                      "pattern": "**.ini",
                                                                      "target": "''' 
                                                    + deploymentLocation + '''/"
                                                                  }
                                                              ]
                                            }'''
                                            )
                                        }
                                    }

                                }
                                
                                  dir ("${WORKSPACE}") {
                                            sh "echo Creating ZIP for cxone"
                                            sh "mkdir -p Cxone"
                                            sh "cp -r apps Cxone"
                                            sh "cp -r *.json Cxone"
                                            zip zipFile: 'Cxone.zip', archive: false, dir: '.'
                                            sh "echo ZIP Created"
                                            stash name: "Cxonefile", includes: "*.zip"
                                        }
                                
                                
                                
                            }
                        }
                    }
                    if (isBlackduck) {
                        stages ["BlackDuckScan"] = {
                            stage("Blackduck scan")
                            {
                                container('maven')
                                {
                                    sh "curl ${BlackDuckDetectUrl} -o /home/jenkins/synopsys-detect-7.13.2.jar"
                                    withCredentials([string(credentialsId: 'black-duck-token', variable: 'blackducktoken')]) {
                                        sh """
						 java -jar /home/jenkins/synopsys-detect-7.13.2.jar \
						 --detect.source.path=${WORKSPACE} \
						 --detect.project.name="${BlackDuckProjectName}" \
						 --detect.project.version.name="${BlackDuckProjectVersion}" \
						 --detect.detector.search.depth=4 \
						 --logging.level.com.blackducksoftware.integration=DEBUG \
						 --blackduck.url=${BlackDuckUrl} \
						 --blackduck.api.token=${blackducktoken}
						 """
                                        sh "rm -rf /home/jenkins/synopsys-detect-7.13.2.jar"
                                    }
                                    /* withCredentials([string(credentialsId: 'black-duck-token', variable: 'blackducktoken')]) {
                          List scanResults = incBlackduck.rapidScan(
                          url: 'https://fis.blackducksoftware.com',
                          credentialsId: "${blackducktoken}",
                          projectName: "${BlackDuckProjectName}",
                          projectVersion: "${BlackDuckProjectVersion}",
                          saveScanResults: true,
                             )
                          }*/
                                }
                            }
                        }
                    }
                    if (isSonar) {
                        stages ["SonarScan"] = {
                            stage ("sonar-scan") {
                                container('maven') {
                                    withCredentials([string(credentialsId: "${SonarQubeCreds}", variable: 'AUTH_TOKEN')]) {
                                        echo "==============================================================================================="
                                        echo "Sonar Scan started"
                                        def pom = readMavenPom file: "pom.xml"
                                        versionNumber = pom.version
                                        echo "Sonar scan"
                                        dir("${env.WORKSPACE}") {
                                            withSonarQubeEnv('sonarqube') {
                                                sh """
									   mvn -V -f pom.xml sonar:sonar \
									   -Dsonar.branch.name=${env.BRANCH_NAME} \
									   -Dsonar.host.url=${SONAR_HOST_URL} \
									   -Dsonar.login=${AUTH_TOKEN} \
									   -DSONAR_USER_HOME=${env.WORKSPACE}
									   """
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if (isCheckmarx) {
                        stages["Checkmarxscan"] = {
                            stage ("Checkmarxscan") {
                                //milestone()
                                sh "dir"
                                step([
                                    $class: 'CxScanBuilder',
                                    comment: "qfscorecompareui - is getting scanned now",
                                    configAsCode: false,
                                    credentialsId: "${checkmarxcred}",
                                    customFields: 'SCID:10000187',
                                    excludeFolders: '',
                                    exclusionsSetting: 'job',
                                    hideDebugLogs: true,
                                    failBuildOnNewResults: false,
                                    failBuildOnNewSeverity: 'HIGH',
                                    filterPattern: ''' !**/_cvs/**/*, !**/.svn/**/*, !**/.hg/**/*, !**/.git/**/*, !**/.bzr/**/*,
                                                        !**/.gitgnore/**/*, !**/.gradle/**/*, !**/.checkstyle/**/*, !**/.classpath/**/*, !**/bin/**/*,
                                                        !**/obj/**/*, !**/backup/**/*, !**/.idea/**/*, !**/*.DS_Store, !**/*.ipr, !**/*.iws,
                                                        !**/*.bak, !**/*.tmp, !**/*.aac, !**/*.aif, !**/*.iff, !**/*.m3u, !**/*.mid, !**/*.mp3,
                                                        !**/*.mpa, !**/*.ra, !**/*.wav, !**/*.wma, !**/*.3g2, !**/*.3gp, !**/*.asf, !**/*.asx,
                                                        !**/*.avi, !**/*.flv, !**/*.mov, !**/*.mp4, !**/*.mpg, !**/*.rm, !**/*.swf, !**/*.vob,
                                                        !**/*.wmv, !**/*.bmp, !**/*.gif, !**/*.jpg, !**/*.png, !**/*.psd, !**/*.tif, !**/*.swf,
                                                        !**/*.jar, !**/*.zip, !**/*.rar, !**/*.exe, !**/*.dll, !**/*.pdb, !**/*.7z, !**/*.gz,
                                                        !**/*.tar.gz, !**/*.tar, !**/*.gz, !**/*.ahtm, !**/*.ahtml, !**/*.fhtml, !**/*.hdm,
                                                        !**/*.hdml, !**/*.hsql, !**/*.ht, !**/*.hta, !**/*.htc, !**/*.htd, !**/*.war, !**/*.ear,
                                                        !**/*.htmls, !**/*.ihtml, !**/*.mht, !**/*.mhtm, !**/*.mhtml, !**/*.ssi, !**/*.stm,
                                                        !**/*.bin,!**/*.lock,!**/*.svg,!**/*.obj,!**/*.js,
                                                        !**/*.stml, !**/*.ttml, !**/*.txn, !**/*.xhtm, !**/*.xhtml, !**/*.class, !**/*.iml, !Checkmarx/Reports/*.*,
                                                        !OSADependencies.json, !**/node_modules/**/*, !**/.cxsca-results.json, !**/.cxsca-sast-results.json, !.checkmarx/cx.config ''',
                                    fullScanCycle: 10,
                                    generatePdfReport: true,
                                    groupId: '1811',
                                    incremental: true,
                                    password: '{AQAAABAAAAAQdLmv18sIAQD9SDCeakvlEdAWH7I61QykGvJQ1mipRDQ=}',
                                    preset: '100000',
                                    projectName: "qf-report_${scan_type}",
                                    sastEnabled: true,
                                    serverUrl: "${checkmarxurl}",
                                    sourceEncoding: '5',
                                    useOwnServerCredentials: true,
                                    username: '',
                                    vulnerabilityThresholdResult: 'FAILURE',
                                    waitForResultsEnabled: true
                                ])
                            }
                        }
                    }
                    if (isCxone) {
                        stages["CxOneScan"] = {
                            stage ("CxOneScan") {
                                node("ds_peng") {
                                    //cleanWs()
                                    //checkout scm
                                    dir ("${WORKSPACE}") {
                                        //powershell(returnStdout: true, script: ''' mkdir cx ''')  
                                        //powershell(returnStdout: true, script: ''' Copy-Item ./* cx -Exclude .git,cx -Recurse ''')
                                        //bat 'cmd.exe'
                                        powershell(returnStdout: true, script: ''' mkdir cx ''')
                                        unstash 'Cxonefile';
                                        bat label: 'compressfile', script: "7z.exe x Cxone.zip -ocx"
                                        // bat 'cmd.exe'
                                        bat """ cx scan create ^
									--project-name ${cxoneprojectname} ^
									--project-groups ${cxoneprojectgroup} ^
									--project-tags ${cxoneprojecttags} ^
									--scan-types sca ^
                                    --tags ${cxoneprojecttags} ^
									--branch ${branchName} -s "${WORKSPACE}"\\cx ^
									--sca-resolver scaResolver ^
									--sca-resolver-params "--ignore-test-dependencies true --ignore-dev-dependencies true -e ${excludeList}" ^
									--debug
								"""
                                    }
                                }
                            }
                        }
                    }
                    parallel(stages)
                }
            }
        }
    }
    if (isDeployDev || isDeployQC) {
        node('ansible') {
            def artifactsURL
            checkout scm
            def artVersion = readMavenPom().version
            if (readMavenPom().version.contains("SNAPSHOT"))
            {
                deployment = "snapshot"
            } else {
                deployment = "release"
            }
            rtServer (id: 'Artifactory-1', url: "${ArtifactoryURL}", credentialsId: 'f70c497a-59ed-4ad9-ac37-86bb4a31bd4a', bypassProxy: true, timeout: 300)
            rtDownload (
                serverId: 'Artifactory-1',
                spec: '''{
                        "files": [
                          {
                            "pattern": "ds-maven-''' + deployment + '''-local/com/fisglobal/qualifile/qfscorecompareui/''' + artVersion + '''/Artifacts-qfscorecompareui-''' + artVersion + '''.ini",
                            "target": "''' + WORKSPACE + '''/",
                            "flat": "true"
                          }
                        ]
                  }'''
            )
            //  artifactsURL = sh(script: "cat ${WORKSPACE}/Artifacts-${artVersion}.ini | grep 'qa'", returnStdout: true).trim()
            //  println "${artifactsURL}"
            if (isDeployDev) {
                //artifactsURL = sh(script: "cat ${WORKSPACE}/Artifacts-${artVersion}.ini | grep -v 'qa'", returnStdout: true).trim()
                //println "${artifactsURL}"
                // stage("Deploy to DEV") {
                //     ansiblePlaybook(
                //         playbook: "playbook.yml",
                //         inventory: "hosts",
                //         limit: "DEV",
                //         credentialsId: "4b23ad30-ff47-492f-9eef-faa8a19466be",
                //         vaultCredentialsId: "1a3f9998-340e-43d1-bf10-02fa7442cad1",
                //          extraVars: [
                //           deployment: deployment,
                //           jobname: branchName,
                //           buildno: buildno,
                //           ArtifactUrl: artifactsURL,
                //           productCode: productCode
                //         ]
                //     )
                // }
                //  stage("Deploy to DEV Apache Webserver") {
                //     ansiblePlaybook(
                //         playbook: "playbook.yml",
                //         inventory: "hosts",
                //         limit: "DEV_WEB",
                //         credentialsId: "4b23ad30-ff47-492f-9eef-faa8a19466be",
                //         vaultCredentialsId: "1a3f9998-340e-43d1-bf10-02fa7442cad1",
                //          extraVars: [
                //           deployment: deployment,
                //           jobname: branchName,
                //           buildno: buildno,
                //           ArtifactUrl: artifactsURL,
                //           productCode: productCode
                //         ]
                //     )
                // }
            }
            if (isDeployQC) {
                fold = sh(script: "cd ${WORKSPACE} && ls -lrt", returnStdout: true).trim()
                println "folder - ${fold}"
                artifactsURL = sh(script: "cat ${WORKSPACE}/Artifacts-qfscorecompareui-${artVersion}.ini | grep 'qa'", returnStdout: true).trim()
                println "articatory url - ${artifactsURL}"
                stage("Deploy to QC Apache Webserver") {
                    milestone()
                    sh 'ansible --version && ansible-galaxy --version'
                    checkout scm
                    ansiblePlaybook(
                        playbook: "playbook.yml",
                        inventory: "hosts",
                        limit: "QC_WEB",
                        //credentialsId: "4e5f6700-b78e-4d10-a9be-296036a288d9",
                        //vaultCredentialsId: "1a3f9998-340e-43d1-bf10-02fa7442cad1",
                      	credentialsId: "4b23ad30-ff47-492f-9eef-faa8a19466be",
                		vaultCredentialsId: "1a3f9998-340e-43d1-bf10-02fa7442cad1",
                        //extras: "-vvv",
                        extraVars: [
                            deployment: deployment,
                            jobname: branchName,
                            buildno: buildno,
                            ArtifactUrl: artifactsURL
                        ]
                    )
                }
            }
        }
    }
}

catch (e) {
    currentBuild.result = "FAILED"
    echo 'BUILD FAILED'
    throw e
}
finally {
    buildNotification {
        emailId = "arun.masta@fisglobal.com"
        echo "Finshed!"
    }
}