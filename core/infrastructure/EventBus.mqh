//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EventBus.mqh                                           |
//| Layer   : Infrastructure                                         |
//+------------------------------------------------------------------+

#ifndef CORE_INFRASTRUCTURE_EVENTBUS_MQH
#define CORE_INFRASTRUCTURE_EVENTBUS_MQH

class CEventBus
{
public:
    void Publish(string eventName)
    {
        Print("[EVENT] ", eventName);
    }

    void Broadcast(string eventName)
    {
        Publish(eventName);
    }
};

#endif