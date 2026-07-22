//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Core.mqh                                               |
//| Layer   : Core                                                   |
//| Version : 4.1.0                                                  |
//| Purpose : Main System Core Controller                            |
//+------------------------------------------------------------------+

#ifndef CORE_CORE_MQH
#define CORE_CORE_MQH


#include "runtime/RuntimeManager.mqh"


//--------------------------------------------------
// Core Controller
//--------------------------------------------------

class CCore
{

private:

    CRuntimeManager m_runtime;


public:


    //--------------------------------------------------
    // Initialize
    //--------------------------------------------------

    bool Initialize()
    {

        if(!m_runtime.Initialize())
            return false;


        return true;

    }



    //--------------------------------------------------
    // Tick
    //--------------------------------------------------

    bool Tick(
        const string symbol,
        ENUM_TIMEFRAMES timeframe)
    {

        m_runtime.OnTick();


        return true;

    }



    //--------------------------------------------------
    // Timer
    //--------------------------------------------------

    void Timer()
    {

        m_runtime.OnTimer();

    }



    //--------------------------------------------------
    // Shutdown
    //--------------------------------------------------

    void Shutdown()
    {

        m_runtime.Shutdown();

    }

};


#endif
//+------------------------------------------------------------------+