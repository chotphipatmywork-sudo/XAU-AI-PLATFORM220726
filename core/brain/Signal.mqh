//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Signal.mqh                                             |
//| Layer   : Brain                                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Standard signal definition                             |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SIGNAL_MQH
#define CORE_BRAIN_SIGNAL_MQH

//--------------------------------------------------
// Signal Type
//--------------------------------------------------

enum ENUM_SIGNAL_TYPE
{
   SIGNAL_NONE = 0,
   SIGNAL_BUY,
   SIGNAL_SELL
};

//--------------------------------------------------
// Signal
//--------------------------------------------------

class CSignal
{
public:

   ENUM_SIGNAL_TYPE type;

   double confidence;

   string source;

   string reason;

   datetime timestamp;

   CSignal()
   {
      type       = SIGNAL_NONE;
      confidence = 0.0;
      source     = "";
      reason     = "";
      timestamp  = TimeCurrent();
   }
};

#endif