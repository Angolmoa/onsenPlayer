from ask import alexa
import onsenInfo as oi

def lambda_handler(request_obj, context=None):
    metadata = {}
    return alexa.route_request(request_obj, metadata)

@alexa.default_handler()
def default_handler(request):
    return alexa.respond('再生したい番組を教えてください').with_card(getStringListOfDay("最新"))


@alexa.request_handler("LaunchRequest")
def launch_request_handler(request):
    return alexa.respond('再生したい番組を教えてください').with_card(getStringListOfDay("最新"))


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