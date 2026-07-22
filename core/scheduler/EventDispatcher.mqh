//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EventDispatcher.mqh                                    |
//| Layer   : Scheduler                                              |
//| Version : 1.2.0                                                  |
//| Purpose : Event Dispatcher with Callback Binding                 |
//+------------------------------------------------------------------+

#ifndef CORE_SCHEDULER_EVENTDISPATCHER_MQH
#define CORE_SCHEDULER_EVENTDISPATCHER_MQH


#include "TickDispatcher.mqh"
#include "TimerDispatcher.mqh"


//--------------------------------------------------
// Event Dispatcher
//--------------------------------------------------

class CEventDispatcher
{

private:

    CTickDispatcher  m_tick;

    CTimerDispatcher m_timer;



public:


    //--------------------------------------------------
    // Register Tick Callback
    //--------------------------------------------------

    void SetTickCallback(
        ITickCallback *callback)
    {
        m_tick.SetCallback(callback);
    }



    //--------------------------------------------------
    // Initialize
    //--------------------------------------------------

    bool Initialize()
    {

        if(!m_tick.Initialize())
        {
            return false;
        }


        if(!m_timer.Initialize())
        {
            return false;
        }


        return true;
    }



    //--------------------------------------------------
    // Tick Event
    //--------------------------------------------------

    void OnTick()
    {
        m_tick.OnTick();
    }



    //--------------------------------------------------
    // Timer Event
    //--------------------------------------------------

    void OnTimer()
    {
        m_timer.OnTimer();
    }



    //--------------------------------------------------
    // Shutdown
    //--------------------------------------------------

    void Shutdown()
    {

        m_tick.Shutdown();

        m_timer.Shutdown();

    }

};


#endif

//+------------------------------------------------------------------+