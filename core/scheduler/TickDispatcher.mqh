//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TickDispatcher.mqh                                     |
//| Layer   : Scheduler                                              |
//| Version : 2.1.0                                                  |
//| Purpose : Tick Event Dispatcher with Callback                   |
//+------------------------------------------------------------------+

#ifndef CORE_SCHEDULER_TICKDISPATCHER_MQH
#define CORE_SCHEDULER_TICKDISPATCHER_MQH


//--------------------------------------------------
// Tick Callback Interface
//--------------------------------------------------

class ITickCallback
{

public:

    virtual void OnTickEvent()
    {
    }

};


//--------------------------------------------------
// Tick Dispatcher
//--------------------------------------------------

class CTickDispatcher
{

private:

    ITickCallback *m_callback;


public:


    //--------------------------------------------------
    // Constructor
    //--------------------------------------------------

    CTickDispatcher()
    {
        m_callback = NULL;
    }



    //--------------------------------------------------
    // Register Callback
    //--------------------------------------------------

    void SetCallback(
        ITickCallback *callback)
    {

        m_callback = callback;

    }



    //--------------------------------------------------
    // Initialize
    //--------------------------------------------------

    bool Initialize()
    {
        return true;
    }



    //--------------------------------------------------
    // Tick Event
    //--------------------------------------------------

    void OnTick()
    {

        Dispatch();

    }



    //--------------------------------------------------
    // Dispatch
    //--------------------------------------------------

    void Dispatch()
    {

        if(m_callback == NULL)
            return;


        m_callback.OnTickEvent();

    }



    //--------------------------------------------------
    // Shutdown
    //--------------------------------------------------

    void Shutdown()
    {

        m_callback = NULL;

    }

};


#endif

//+------------------------------------------------------------------+