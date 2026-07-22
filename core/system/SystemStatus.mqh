//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SystemStatus.mqh                                       |
//| Layer   : Core / System                                          |
//| Version : 1.0.0                                                  |
//| Purpose : System Runtime Status                                  |
//+------------------------------------------------------------------+

#ifndef CORE_SYSTEM_SYSTEMSTATUS_MQH
#define CORE_SYSTEM_SYSTEMSTATUS_MQH

//--------------------------------------------------
// System State
//--------------------------------------------------

enum ENUM_SYSTEM_STATUS
{
    SYSTEM_STATUS_UNKNOWN = 0,
    SYSTEM_STATUS_STARTING,
    SYSTEM_STATUS_READY,
    SYSTEM_STATUS_RUNNING,
    SYSTEM_STATUS_STOPPED,
    SYSTEM_STATUS_ERROR
};

//--------------------------------------------------
// System Status
//--------------------------------------------------

class CSystemStatus
{

private:
    ENUM_SYSTEM_STATUS m_status;

    datetime m_lastTick;

    datetime m_startTime;

    int m_tickCount;

    string m_lastError;

public:
    //--------------------------------------------------
    // Constructor
    //--------------------------------------------------

    CSystemStatus()
    {
        Reset();
    }

    //--------------------------------------------------
    // Reset
    //--------------------------------------------------

    void Reset()
    {

        m_status = SYSTEM_STATUS_UNKNOWN;

        m_lastTick = 0;

        m_startTime = 0;

        m_tickCount = 0;

        m_lastError = "";
    }

    //--------------------------------------------------
    // Start
    //--------------------------------------------------

    void Start()
    {

        m_status = SYSTEM_STATUS_STARTING;

        m_startTime = TimeCurrent();
    }

    //--------------------------------------------------
    // Ready
    //--------------------------------------------------

    void Ready()
    {
        m_status = SYSTEM_STATUS_READY;
    }

    //--------------------------------------------------
    // Tick Update
    //--------------------------------------------------

    void UpdateTick()
    {

        m_status = SYSTEM_STATUS_RUNNING;

        m_lastTick = TimeCurrent();

        m_tickCount++;
    }

    //--------------------------------------------------
    // Error
    //--------------------------------------------------

    void SetError(string error)
    {

        m_status = SYSTEM_STATUS_ERROR;

        m_lastError = error;
    }

    //--------------------------------------------------
    // Stop
    //--------------------------------------------------

    void Stop()
    {
        m_status = SYSTEM_STATUS_STOPPED;
    }

    //--------------------------------------------------
    // Getters
    //--------------------------------------------------

    ENUM_SYSTEM_STATUS Status()
    {
        return m_status;
    }

    datetime LastTick()
    {
        return m_lastTick;
    }

    int TickCount()
    {
        return m_tickCount;
    }

    string LastError()
    {
        return m_lastError;
    }
};

#endif
//+------------------------------------------------------------------+