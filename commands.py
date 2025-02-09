import asyncio
import sys
import traceback

client = None

class Event: #Class to store event data
    def __init__(self, f, triggerType, name, **kwargs):
        self.handler = f
        self.name=name
        self.triggerType = triggerType
            

triggerHandlers = {
    "\\message" : {},
    "\\messageNoBot" : {},
    "\\command" : {},
    "\\commandNotFound" : {},
    "\\channelUpdate" : {},
    "\\botException" : {},
    "\\set_root_context_on_load" : {},
    "\\timeTick" : {},
    "\\reactionAdded" : {},
    "\\reactionRemoved" : {},
    "\\messageEdit": {}
}

helpString = ""

def messageHandlerFilter(triggerFilter, filterType="eq"):
    def decorator(func):
        if filterType=="eq":
            async def handler(triggerMessage):
                if triggerMessage.content == triggerFilter:
                    await func(triggerMessage)
            return handler
        elif filterType=="contains":
            async def handler(triggerMessage):
                if triggerFilter in triggerMessage.content:
                    await func(triggerMessage)
            return handler
        elif filterType=="cqc":
            async def handler(triggerMessage):
                if triggerFilter in triggerMessage.content.lower():
                    await func(triggerMessage)
            return handler
    return decorator
    
commandMutexes = []

def registerEventHandler(triggerType="\\command", name=None, helpText=None, exclusivity=None, **kwargs):
    """Decorator that registers event handlers
    Stay tuned for kwargs
    """
    def decorator(f):
        if exclusivity == "global" and name is not None:
            print("Global exclusive command " + name)
            async def excluder(triggerMessage):
                global commandMutexes
                print(commandMutexes)
                if name not in commandMutexes:
                    commandMutexes.append(name)
                    print("Locked " + name)
                    try:
                        await f(triggerMessage)
                    except:
                        raise
                    finally:
                        commandMutexes.remove(name)
                        print("Unlocked " + name)
                else:
                    await triggerMessage.channel.send( "One at a time please")
            event = Event(excluder, triggerType, name, **kwargs)
        else:
            event = Event(f, triggerType, name, **kwargs)
        if triggerType in triggerHandlers:
            if helpText is not None:
                global helpString
                helpString += helpText + "\n"
            if name is not None:
                if name in triggerHandlers[triggerType]:
                    print("Duplicate command", name)
                triggerHandlers[triggerType].update({name : event})
            else:
                triggerHandlers[triggerType].update({f.__name__, event})
        else:
            print("Invalid trigger type registered ", str(triggerType))
            
        return f
    return decorator
    
async def executeEvent(triggerType="\\command", name=None, **kwargs):
    if not triggerType in triggerHandlers:
        print("Called with invalid event type " + triggerType)
        return
        
    if name is not None:
        #print(triggerType + " " + name)
        try:
            if triggerType == "\\command" and not name in triggerHandlers[triggerType]:
                await executeEvent(triggerType="\\commandNotFound", name=None, **kwargs)
            else:       
                await triggerHandlers[triggerType][name].handler(**kwargs)
        except:
            if sys.exc_info()[0].__name__ != "RestartException":
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("Unexpected error:", exc_value)
                traceback.print_tb(exc_traceback)
#               tb = str.join("", traceback.format_exception(exc_type, exc_value, exc_traceback))
#               channel = client.get_channel(124051195949088768)
#               await channel.send("```" + tb + "```")
            else: 
                raise
            
    else:
        for k, v in triggerHandlers[triggerType].items():
            #print("Running " + k)
            await v.handler(**kwargs)