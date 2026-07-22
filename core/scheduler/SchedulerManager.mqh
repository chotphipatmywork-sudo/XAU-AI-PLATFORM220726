//+------------------------------------------------------------------+

#ifndef CORE_SCHEDULER_SCHEDULERMANAGER_MQH
#define CORE_SCHEDULER_SCHEDULERMANAGER_MQH

#include "Scheduler.mqh"

class CSchedulerManager
{
private:
    CScheduler m_scheduler;

public:
    void Tick()
    {
        m_scheduler.Tick();
    }

    void Timer()
    {
        m_scheduler.Timer();
    }
};

#endif