//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SystemController.mqh                                   |
//| Layer   : Core / Application                                     |
//| Version : 2.0.0                                                  |
//| Purpose : System Lifecycle Controller                            |
//+------------------------------------------------------------------+

#ifndef CORE_APPLICATION_SYSTEMCONTROLLER_MQH
#define CORE_APPLICATION_SYSTEMCONTROLLER_MQH


#include "../runtime/RuntimeManager.mqh"


//--------------------------------------------------
// System State
//--------------------------------------------------

enum ENUM_SYSTEM_STATE
{
    SYSTEM_STOPPED = 0,
    SYSTEM_READY,
    SYSTEM_RUNNING,
    SYSTEM_ERROR
};


//--------------------------------------------------
// System Controller
//--------------------------------------------------

class CSystemController
{

private:

    CRuntimeManager m_runtime;

    ENUM_SYSTEM_STATE m_state;


public:


    //--------------------------------------------------
    // Constructor
    //--------------------------------------------------

    CSystemController()
    {
        m_state = SYSTEM_STOPPED;
    }



    //--------------------------------------------------
    // Initialize
    //--------------------------------------------------

    bool Initialize()
    {

        if(!m_runtime.Initialize())
        {
            m_state = SYSTEM_ERROR;
            return false;
        }


        m_state = SYSTEM_READY;


        return true;
    }



    //--------------------------------------------------
    // Start
    //--------------------------------------------------

    bool Start()
    {

        if(m_state != SYSTEM_READY)
            return false;


        m_state = SYSTEM_RUNNING;


        return true;
    }



    //--------------------------------------------------
    // Tick
    //--------------------------------------------------

    void OnTick()
    {

        if(m_state != SYSTEM_RUNNING)
            return;


        m_runtime.OnTick();

    }



    //--------------------------------------------------
    // Timer
    //--------------------------------------------------

    void OnTimer()
    {

        if(m_state != SYSTEM_RUNNING)
            return;


        m_runtime.OnTimer();

    }



    //--------------------------------------------------
    // Shutdown
    //--------------------------------------------------

    void Shutdown()
    {

        m_runtime.Shutdown();


        m_state = SYSTEM_STOPPED;

    }



    //--------------------------------------------------
    // State
    //--------------------------------------------------

    ENUM_SYSTEM_STATE State()
    {
        return m_state;
    }

};


#endif
//+------------------------------------------------------------------+