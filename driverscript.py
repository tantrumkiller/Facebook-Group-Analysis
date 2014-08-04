import GenrateAnalytics

AccessToken="CAACEdEose0cBADuoK6cAOFmZCKfdR2DtASf3zK7I5XwNasvpll3zUapGNCGEyaA8bhNl4pNAnAzhEsLCaGu9bwcu2KrQ7CDmf8hAxm8cqT2EZAEixdpIwyyn9604ZBJOzOg9E3YBozw0cjy1Y5YbSlY9Detb7054ZCAbzdlzZCe1icVAdrSZCZCQ3ffByKtVMhnkZBbZBe9hrpAZDZD"
GroupId = "137485186370009"

# this graph api may change
request_url = "https://graph.facebook.com/"+GroupId+"/feed?&access_token="+AccessToken

GenrateAnalytics.installProxy('j.kshitiz','dEtKD3Cx','202.141.80.19','3128')
users = GenrateAnalytics.populateData(request_url,"time_logs",AccessToken)
GenrateAnalytics.dumpData("stupid_intel",users)
