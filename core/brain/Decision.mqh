//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Decision.mqh                                           |
//| Layer   : Brain                                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Brain decision object                                  |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_DECISION_MQH
#define CORE_BRAIN_DECISION_MQH

#include "Signal.mqh"

//--------------------------------------------------
// Decision
//--------------------------------------------------

class CDecision
{
private:

   CSignal m_signal;

public:

   void SetSignal(const CSignal &signal)
   {
      m_signal = signal;
   }

   CSignal GetSignal() const
   {
      return m_signal;
   }

   bool IsBuy() const
   {
      return (m_signal.type == SIGNAL_BUY);
   }

   bool IsSell() const
   {
      return (m_signal.type == SIGNAL_SELL);
   }

   bool IsNone() const
   {
      return (m_signal.type == SIGNAL_NONE);
   }
};

#endif