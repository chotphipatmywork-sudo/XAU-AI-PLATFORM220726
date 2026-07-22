//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeStateMachine.mqh                                  |
//| Layer   : Core / Trade                                           |
//| Version : 1.0.1                                                  |
//| Purpose : Trade State Machine                                    |
//+------------------------------------------------------------------+

#ifndef CORE_TRADE_TRADESTATEMACHINE_MQH
#define CORE_TRADE_TRADESTATEMACHINE_MQH

#include "models/TradeState.mqh"

//--------------------------------------------------

class CTradeStateMachine
{
private:

   CTradeState m_state;

public:

   //--------------------------------------------------

   void Reset()
   {
      m_state.Reset();
   }

   //--------------------------------------------------

   void Initialize(
      const ulong ticket,
      const string symbol,
      const double volume,
      const double entryPrice,
      const double stopLoss,
      const double takeProfit)
   {
      m_state.Reset();

      m_state.Ticket     = ticket;
      m_state.Symbol     = symbol;
      m_state.Volume     = volume;
      m_state.EntryPrice = entryPrice;
      m_state.StopLoss   = stopLoss;
      m_state.TakeProfit = takeProfit;

      m_state.State      = TRADE_STATE_OPEN;
      m_state.Active     = true;
   }

   //--------------------------------------------------

   void SetState(
      ENUM_TRADE_STATE state)
   {
      m_state.State = state;
   }

   //--------------------------------------------------

   void UpdateProfit(
      const double profit)
   {
      m_state.Profit = profit;
   }

   //--------------------------------------------------

   ENUM_TRADE_STATE GetState() const
   {
      return m_state.State;
   }

   //--------------------------------------------------

   bool IsActive() const
   {
      return m_state.Active;
   }

   //--------------------------------------------------

   void Close()
   {
      m_state.State  = TRADE_STATE_CLOSED;
      m_state.Active = false;
   }

   //--------------------------------------------------

   CTradeState GetSnapshot() const
   {
      return m_state;
   }

};

#endif