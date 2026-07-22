//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionLifecycle.mqh                                  |
//| Layer   : Core / Position                                        |
//| Version : 1.0.0                                                  |
//| Purpose : Position Lifecycle Manager                             |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONLIFECYCLE_MQH
#define CORE_POSITION_POSITIONLIFECYCLE_MQH

#include "PositionTracker.mqh"
#include "PositionUpdater.mqh"

#include "models/PositionSnapshot.mqh"

//--------------------------------------------------

class CPositionLifecycle
{
private:
    CPositionTracker m_tracker;
    CPositionUpdater m_updater;

public:
    //--------------------------------------------------

    bool Process(
        const string symbol,
        CPositionSnapshot &snapshot)
    {
        if (!m_tracker.Capture(symbol, snapshot))
            return false;

        m_updater.Update(snapshot);

        return true;
    }
};

#endif