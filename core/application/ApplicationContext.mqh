//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ApplicationContext.mqh                                 |
//| Layer   : Core / Application                                     |
//| Version : 1.0.0                                                  |
//| Purpose : Application Runtime Context                            |
//+------------------------------------------------------------------+

#ifndef CORE_APPLICATION_APPLICATIONCONTEXT_MQH
#define CORE_APPLICATION_APPLICATIONCONTEXT_MQH

//--------------------------------------------------
// Application State
//--------------------------------------------------

enum ENUM_APPLICATION_STATE
{
    APP_STATE_IDLE = 0,
    APP_STATE_INITIALIZING,
    APP_STATE_RUNNING,
    APP_STATE_STOPPING,
    APP_STATE_ERROR
};

//--------------------------------------------------
// Application Context
//--------------------------------------------------

class CApplicationContext
{

private:
    ENUM_APPLICATION_STATE m_state;

    datetime m_startTime;

    bool m_initialized;

public:
    //--------------------------------------------------

    CApplicationContext()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        m_state = APP_STATE_IDLE;

        m_startTime = 0;

        m_initialized = false;
    }

    //--------------------------------------------------

    void Initialize()
    {
        m_state = APP_STATE_INITIALIZING;

        m_startTime = TimeCurrent();

        m_initialized = true;

        m_state = APP_STATE_RUNNING;
    }

    //--------------------------------------------------

    void Shutdown()
    {
        m_state = APP_STATE_STOPPING;

        m_initialized = false;

        m_state = APP_STATE_IDLE;
    }

    //--------------------------------------------------

    bool IsInitialized() const
    {
        return m_initialized;
    }

    //--------------------------------------------------

    ENUM_APPLICATION_STATE State() const
    {
        return m_state;
    }

    //--------------------------------------------------

    datetime StartTime() const
    {
        return m_startTime;
    }

    //--------------------------------------------------

    bool IsRunning() const
    {
        return (
            m_state == APP_STATE_RUNNING);
    }
};

#endif
//+------------------------------------------------------------------+