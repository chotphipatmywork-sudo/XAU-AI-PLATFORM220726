//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EventLoop.mqh                                          |
//| Layer   : Core / Scheduler                                       |
//| Version : 1.1.0                                                  |
//| Purpose : Main Event Loop Controller with Callback               |
//+------------------------------------------------------------------+

#ifndef CORE_SCHEDULER_EVENTLOOP_MQH
#define CORE_SCHEDULER_EVENTLOOP_MQH


#include "EventDispatcher.mqh"


//--------------------------------------------------
// Event Loop
//--------------------------------------------------

class CEventLoop
{

private:

    CEventDispatcher m_dispatcher;



public:


    //--------------------------------------------------
    // Register Tick Callback
    //--------------------------------------------------

    void SetTickCallback(
        ITickCallback *callback)
    {

        m_dispatcher.SetTickCallback(callback);

    }



    //--------------------------------------------------
    // Initialize
    //--------------------------------------------------

    bool Initialize()
    {
        return m_dispatcher.Initialize();
    }



    //--------------------------------------------------
    // Tick Event
    //--------------------------------------------------

    void OnTick()
    {
        m_dispatcher.OnTick();
    }



    //--------------------------------------------------
    // Timer Event
    //--------------------------------------------------

    void OnTimer()
    {
        m_dispatcher.OnTimer();
    }



    //--------------------------------------------------
    // Shutdown
    //--------------------------------------------------

    void Shutdown()
    {
        m_dispatcher.Shutdown();
    }

};


#endif

//+------------------------------------------------------------------+