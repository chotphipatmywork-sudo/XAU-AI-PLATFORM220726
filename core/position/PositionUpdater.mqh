//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionUpdater.mqh                                    |
//| Layer   : Core / Position                                        |
//| Version : 1.0.0                                                  |
//| Purpose : Update Position State                                  |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONUPDATER_MQH
#define CORE_POSITION_POSITIONUPDATER_MQH

#include "models/PositionSnapshot.mqh"

//--------------------------------------------------

class CPositionUpdater
{
public:
    //--------------------------------------------------

    void Update(CPositionSnapshot &snapshot)
    {
        if (!snapshot.Valid)
            return;

        // Reserved for future:
        // - Trailing Stop
        // - Break Even
        // - Partial Close
        // - Dynamic TP/SL
    }
};

#endif