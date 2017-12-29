from ask import alexa
import onsenInfo as oi

def lambda_handler(request_obj, context=None):
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

@alexa.intent_handler('PlayIntent')
def play_intent_handler(request):
    day = request.get_slot_value("day")
    num = request.get_slot_value("num")
    if num == None:
        num=1
    num=int(num)-1
    info=oi.getPlayInfoOfDayNum(day,num)
    return alexa.audio_play_response(url=info["moviePath"]["pc"])

@alexa.intent_handler('PlayDayIntent')
def play_intent_handler(request):
    day = request.get_slot_value("day")
    info=oi.getPlayInfoOfDayNum(day,0)
    return alexa.audio_play_response(url=info["moviePath"]["pc"])
    
@alexa.intent_handler('AMAZON.StopIntent')
def audio_stop_intent_handler(request):
    return alexa.audio_stop_response()

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
