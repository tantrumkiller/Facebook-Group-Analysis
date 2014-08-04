import json
import urllib2
import numpy as np
import re

class userStats:
    'This class will contain the information about the user'
    def __init__(self,fb_id,fb_name):
        self.fb_ID = fb_id
        self.fb_name = fb_name

        self.num_posts=0
        self.num_comments=0
        
        self.likes_on_posts=0
        self.likes_on_comments=0
        self.comments_on_posts=0

        self.num_words_comments=0
        self.num_words_post=0

        self.likes_genrated=0; #only posts
        
class fbAccess:
    def __init__(self,AccessToken):
        self.AccessToken = AccessToken
    def pagingRequest(self,paging_url):
        while True:
            # extract access token from the request
            partition1 = paging_url.partition("access_token=")
            partition2 = partition1[2].partition("&")
    
            # if tokens do not matched reconfigure request            
            if(partition2[0]!=self.AccessToken):
                paging_url=partition1[0]+partition1[1]+self.AccessToken+partition2[1]+partition2[2]

            try:
                new_response = urllib2.urlopen(paging_url)
                new_json_string = new_response.read()
                new_feed = json.loads(new_json_string)
                new_response.close()
                return new_feed
            except urllib2.HTTPError as e:
                print e.code
                error_feed  = json.loads(e.read())
                print error_feed['error']['message']
                print "Some Problem with Facebook Access:"
                self.AccessToken = raw_input("Try A New Access Token:")
            except urllib2.URLError as e:
                wait=raw_input("\nLost Internet connection Press Enter When connection is Back.")
            except ValueError as e:
                print "Recived invalid JSON Object, querying again."
            except:
                print "Unrecognized Error Occured"
                # give option to exit or continue
                wait=raw_input("Press c to continue any thing else to exit now:")
                if not wait=='c':
                    return {}
                
                
def populateData(init_request,timelog_filename,AccessToken):
    fb = fbAccess(AccessToken)
    print "Querying facebook for initial list of posts",
    feed = fb.pagingRequest(init_request)
    print "... Data Recived"
    post_count=0
    contributers = {}
    #open a file for appending time info
    time_logs = open(timelog_filename+".txt",'w')

    while 'data' in feed.keys():
        for post in feed['data']:
            post_count+=1
            post_author_name=post['from']['name']
            post_author_ID=post['from']['id']
            print "Analysing Post #",post_count,"by:",post_author_name

            # Author
            if post_author_ID in contributers.keys():
                contributers[post_author_ID].num_posts+=1
            else:
                new_contributer=userStats(post_author_ID,post_author_name)
                contributers[post_author_ID] = new_contributer
                new_contributer.num_posts+=1

            # Time
            if 'created_time' in post.keys():
                time_logs.write(post['created_time']+'\n')

                
            # Word Count
            if 'message' in post.keys():
                msg = post['message']
                wordList = re.split("\.|\s|#|\*|,",msg)
                wordList = filter(None,wordList)
                contributers[post_author_ID].num_words_post+=len(wordList)

            # Likes
            if 'likes' in post.keys() and 'data' in post['likes'].keys():
                like_feed=post['likes']
                while 'data' in like_feed.keys():
                    contributers[post_author_ID].likes_on_posts+=len(like_feed['data'])
                    for liker in like_feed['data']:
                        liker_name=liker['name']
                        liker_id=liker['id']
                        if liker_id in contributers.keys():
                            contributers[liker_id].likes_genrated+=1
                        else:
                            new_liker = userStats(liker_id,liker_name)
                            contributers[liker_id]=new_liker
                            new_liker.likes_genrated+=1

                    # like paging
                    if 'paging' in like_feed and 'next' in like_feed['paging'].keys():
                        print "Querying facebook for more likes on this post",
                        like_feed = fb.pagingRequest(like_feed['paging']['next'])
                        if like_feed=={}:
                            return contributers
                        print "... Data Recived"
                        
                    else:
                        like_feed={}
                        print "No more likes to explore"
            else:
                print "Post has no likes"

            # Comments                    
            if 'comments' in post.keys():
                comment_feed = post['comments']
                while 'data' in comment_feed.keys():
                    contributers[post_author_ID].comments_on_posts+=len(comment_feed['data'])
                    for comment in comment_feed['data']:
                        # author
                        commenter_id=comment['from']['id']
                        if commenter_id in contributers.keys():
                            contributers[commenter_id].num_comments+=1
                        else:
                            new_commenter=userStats(commenter_id,comment['from']['name'])
                            contributers[commenter_id]=new_commenter
                            new_commenter.num_comments+=1

                        # time
                        if 'created_time' in comment.keys():
                            time_logs.write(comment['created_time']+'\n')
                                
                        # word count
                        if 'message' in comment.keys():
                            msg = comment['message']
                            wordList = re.split("\.|\s|#|\*|,",msg)
                            wordList = filter(None,wordList)
                            contributers[commenter_id].num_words_comments+=len(wordList)
                                
                        # likes
                        if 'like_count' in comment.keys():
                            contributers[commenter_id].likes_on_comments+=comment['like_count']

                    # comment paging
                    if 'paging' in comment_feed and 'next' in comment_feed['paging'].keys():
                        print "Querying facebook for more comments on this post",
                        comment_feed = fb.pagingRequest(comment_feed['paging']['next'])                        
                        if comment_feed=={}:
                            return contributers
                        print "... Data Recived"
                        
                    else:
                        comment_feed={}
                        print "No more comments to explore"
                    
            else:
                print "Post has no comments"         

        # post paging
        if 'paging' in feed and 'next' in feed['paging'].keys():
            print "Querying facebook for more posts",
            feed = fb.pagingRequest(feed['paging']['next'])
            if feed=={}:
                return contributers
            print "... Data Recived"
            
        else:
            print "No more posts to analyse"
            feed={}

    time_logs.close()
    return contributers

def dumpData(filename,users):
    user_data = open(filename+".csv",'w')
    #dump data in a csv
    user_data.write("Name,Posts,Comments,Comments Recived,Likes:Posts,Likes:Comments,Likes:Genrated,Words:Posts,Words:Comments\n")
    for user_id in users.keys():
            try:
                user=users[user_id]
                user_data.write(str(user.fb_name)+",")
                user_data.write(str(user.num_posts)+",")
                user_data.write(str(user.num_comments)+",")
                user_data.write(str(user.comments_on_posts)+",")
                user_data.write(str(user.likes_on_posts)+",")
                user_data.write(str(user.likes_on_comments)+",")
                user_data.write(str(user.likes_genrated)+",")
                user_data.write(str(user.num_words_post)+",")
                user_data.write(str(user.num_words_comments)+"\n")
            except UnicodeEncodeError:
                print "Unrecognized characters, ignoring user."
                
    user_data.close()

def installProxy(username,password,host,port):
    proxyHandler = urllib2.ProxyHandler({'https': 'https://'+username+':'+password+'@'+host+':'+port})
    proxyOpener = urllib2.build_opener(proxyHandler)
    urllib2.install_opener(proxyOpener)

