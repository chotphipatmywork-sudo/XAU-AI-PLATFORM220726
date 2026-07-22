//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionMonitor.mqh                                    |
//| Layer   : Core / Position                                        |
//| Version : 1.1.0                                                  |
//| Purpose : Position Monitor                                       |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONMONITOR_MQH
#define CORE_POSITION_POSITIONMONITOR_MQH

#include "models/PositionResult.mqh"

//--------------------------------------------------
// Position Monitor
//--------------------------------------------------

class CPositionMonitor
{
public:

   //--------------------------------------------------

   void Update(
      CPositionResult &result)
   {

      if(!result.Valid)
         return;


      if(result.Status != POSITION_FOUND)
         return;


      //--------------------------------------------------
      // Future Position Monitoring
      //--------------------------------------------------
      //
      // - Trailing Stop
      // - Break Even
      // - Partial Close
      // - Time Exit
      // - Profit Lock
      //

   }

};

#endif