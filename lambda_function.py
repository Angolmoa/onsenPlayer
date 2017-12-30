from ask import alexa
import onsenInfo as oi

help_msg="「月曜の1番を再生」など曜日と番号を指定します。\n「月曜の番組一覧」などで各曜日の番組リストを取得できます。"

def lambda_handler(request_obj, context=None):
    print(request_obj)
    metadata = {}
    return alexa.route_request(request_obj, metadata)

@alexa.default_handler()
def default_handler(request):
    card = alexa.create_card(title="最新の番組一覧", subtitle=None,
                             content=oi.getStringListOfDay("最新"))    
    return alexa.create_response('再生したい番組を教えてください',
                                 end_session=False, card_obj=card)

@alexa.request_handler("LaunchRequest")
def launch_request_handler(request):
    card = alexa.create_card(title="最新の番組一覧", subtitle=None,
                             content=oi.getStringListOfDay("最新"))    
    return alexa.create_response('再生したい番組を教えてください',
                                 end_session=False, card_obj=card)

@alexa.request_handler("SessionEndedRequest")
def session_ended_request_handler(request):
    return alexa.create_response(message="Goodbye!")

@alexa.intent_handler('GetChannelListIntent')
def get_channel_list_intent_handler(request):
    day = request.slots["day"]
    print(request.slots["day"])
    print(day)
    if day == None:
        return alexa.create_response("Could not find an ingredient!")
    d=oi.getDayId(day)
    titles={}
    if d == "latest" :
        titles = oi.getNewTitle()
    else:
        titles = oi.getTitleOfDay(d)
    card_content=oi.getStringListOfDay(day,titles)
    speech_content=oi.getStringListOfDay(day,titles,True)
    card = alexa.create_card(title="{0}の番組一覧".format(day), subtitle=None,
                             content=card_content)    
    return alexa.create_response(speech_content,
                                 end_session=False, card_obj=card)

@alexa.intent_handler('GetDetailIntent')
def get_detail_info_intent_handler(request):
    day = request.get_slot_value("day")
    num = request.get_slot_value("num")
    if num == None:
        num=1
    num=int(num)-1
    info = oi.getTitleInfoOfDayNum(day,num)
    print(info)
    card_text="{0}\nパーソナリティー {1}".format(info["update"],info["personality"])
    if not info["guest"] == None:
        card_text+="\nゲストは {0}".format(info["guest"])
    card_image = { "smallImageUrl" : info["thumbnail"] , "largeImageUrl" : info["thumbnail"] } #image指定はalexa_io.pyを拡張
    speech_content="{0} {1}".format(info["data-kana"],card_text)
    card = alexa.create_card(title="{0}".format(info["title"]),
                             text=card_text, card_type="Standard", image=card_image)
    
    return alexa.create_response(speech_content,
                                 end_session=False, card_obj=card)

def play_day_num(day,num,endSession=False):
    info=oi.getPlayInfoOfDayNum(day,num)
    if info==None:
        return None, None
    if len(info["moviePath"]["pc"])>0:
        return alexa.audio_play_response(url=info["moviePath"]["pc"],day=day,num=num), info["title"]
    return None, info["title"]

@alexa.intent_handler('PlayIntent')
def play_intent_handler(request):
    day = request.get_slot_value("day")
    num = request.get_slot_value("num")
    if num == None:
        num=1
    num=int(num)-1
    res, title = play_day_num(day,num)
    if res==None:
        if title==None:
            return alexa.create_response("{0} {1}は無効な番組です".format(day,num+1), end_session=False)
        return alexa.create_response("{0}は再生できない番組です".format(title), end_session=False)
    return res

@alexa.intent_handler('PlayDayIntent')
def play_day_intent_handler(request):
    day = request.get_slot_value("day")
    info=oi.getPlayInfoOfDayNum(day,0)
    res, title = play_day_num(day,num)
    if res==None:
        if title==None:
            return alexa.create_response("{0} {1}は無効な番組です".format(day,num+1), end_session=False)
        return alexa.create_response("{0}は再生できない番組です".format(title), end_session=False)
    return res

def play_next(day,num,endSession=True):
    res,title=play_day_num(day,num+1,endSession)
    if res==None:
        if title==None:
            return alexa.create_response(end_session=True)
        return enqueue_next(day,0,endSession)
    return res

@alexa.intent_handler('AMAZON.NextIntent')
def audio_next_intent_handler(request):
    token = request.get_token().split(",")
    day = token[0]
    num = int(token[1])
    return play_next(day,num,endSession=True)

def enqueue_day_num(day,num):
    info=oi.getPlayInfoOfDayNum(day,num)
    if info==None:
        return None
    if len(info["moviePath"]["pc"])>0:
        return alexa.audio_play_response(url=info["moviePath"]["pc"],day=day,num=num,playBehavior="ENQUEUE",endSession=True)
    return None

def enqueue_next(day,num):
    res=enqueue_day_num(day,num+1)
    if res==None:
        if num==0:
            return alexa.create_response(end_session=True)
        return enqueue_next(day,0)
    return res

@alexa.request_handler('AudioPlayer.PlaybackNearlyFinished')
def playback_nearly_finished_request_handler(request):
    token = request.get_token().split(",")
    day = token[0]
    num = int(token[1])
    return enqueue_next(day,num)

@alexa.request_handler('AudioPlayer.PlaybackStarted')
def playback_started_request_handler(request):
    return alexa.create_response(end_session=True)

@alexa.intent_handler('AMAZON.StopIntent')
def audio_stop_intent_handler(request):
    return alexa.audio_stop_response()
    
@alexa.intent_handler('AMAZON.PauseIntent')
def audio_pause_intent_handler(request):
    return alexa.audio_stop_response()
    
@alexa.intent_handler('AMAZON.ResumeIntent')
def audio_resume_intent_handler(request):
    return alexa.audio_resume_response()
    
@alexa.intent_handler('AMAZON.HelpIntent')
def help_intent_handler(request):
    card = alexa.create_card(title="つかいかた",
                             text=help_msg)    
    return alexa.create_response(help_msg,
                                 end_session=False, card_obj=card)

if __name__ == "__main__":    
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve','-s', action='store_true', default=False)
    args = parser.parse_args()
    
    if args.serve:        
        ###
        # This will only be run if you try to run the server in local mode 
        ##
        print('Serving ASK functionality locally.')
        import flask
        server = flask.Flask(__name__)
        @server.route('/')
        def alexa_skills_kit_requests():
            request_obj = flask.request.get_json()
            return lambda_handler(request_obj)
        server.run()
