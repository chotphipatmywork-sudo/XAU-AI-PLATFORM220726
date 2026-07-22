//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainContextBuilder.mqh                                |
//| Layer   : Core / Brain                                           |
//| Version : 2.2.1                                                  |
//| Purpose : Build Brain Context                                    |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_BRAINCONTEXTBUILDER_MQH
#define CORE_BRAIN_BRAINCONTEXTBUILDER_MQH

#include "../data/DataManager.mqh"

#include "trend/models/TrendContext.mqh"

#include "volatility/models/VolatilityContext.mqh"

#include "liquidity/models/LiquidityContext.mqh"

#include "session/models/SessionContext.mqh"

#include "ClosedBarObservationTime.mqh"


//--------------------------------------------------

class CBrainContextBuilder
{
private:

   CDataManager m_data;
   CClosedBarObservationTime m_observation_time;

public:

   //--------------------------------------------------
   // Trend
   //--------------------------------------------------

   CTrendContext BuildTrendContext(
      const string symbol,
      ENUM_TIMEFRAMES timeframe,
      const int shift=0)
   {
      CTrendContext context;

      context.Reset();

      context.Symbol    = symbol;
      context.Timeframe = timeframe;
      context.Shift     = shift;

      context.Close = m_data.GetClose(symbol,timeframe,shift);
      context.Open  = m_data.GetOpen(symbol,timeframe,shift);
      context.High  = m_data.GetHigh(symbol,timeframe,shift);
      context.Low   = m_data.GetLow(symbol,timeframe,shift);

      context.Bars  = m_data.Bars(symbol,timeframe);

      return context;
   }

   //--------------------------------------------------
   // Volatility
   //--------------------------------------------------

   CVolatilityContext BuildVolatilityContext(
      const string symbol,
      ENUM_TIMEFRAMES timeframe,
      const int shift=0)
   {
      CVolatilityContext context;

      context.Symbol    = symbol;
      context.Timeframe = timeframe;
      context.Shift     = shift;
      context.Bars      = m_data.Bars(symbol,timeframe);

      return context;
   }

   //--------------------------------------------------
   // Liquidity
   //--------------------------------------------------

   CLiquidityContext BuildLiquidityContext(
      const string symbol,
      ENUM_TIMEFRAMES timeframe,
      const int shift=0)
   {
      CLiquidityContext context;

      context.Symbol    = symbol;
      context.Timeframe = timeframe;

      context.Bars      = m_data.Bars(symbol,timeframe);
      context.Shift     = shift;
      context.High      = m_data.GetHigh(symbol,timeframe,shift);
      context.Low       = m_data.GetLow(symbol,timeframe,shift);
      context.Close     = m_data.GetClose(symbol,timeframe,shift);
      context.Volume    = (double)m_data.GetVolume(symbol,timeframe,shift);

      double volume_sum=0.0;
      context.ReferenceHigh=m_data.GetHigh(symbol,timeframe,shift+1);
      context.ReferenceLow=m_data.GetLow(symbol,timeframe,shift+1);
      for(int lookback=1; lookback<=10; lookback++)
        {
         const double high=m_data.GetHigh(symbol,timeframe,context.Shift+lookback);
         const double low=m_data.GetLow(symbol,timeframe,context.Shift+lookback);
         if(high>context.ReferenceHigh)
            context.ReferenceHigh=high;
         if(context.ReferenceLow==0.0 || low<context.ReferenceLow)
            context.ReferenceLow=low;
         volume_sum+=(double)m_data.GetVolume(symbol,timeframe,context.Shift+lookback);
        }
      context.AverageVolume=volume_sum/10.0;

      return context;
   }

   //--------------------------------------------------
   // Session
   //--------------------------------------------------

   CSessionContext BuildSessionContext(
   const string symbol,
   ENUM_TIMEFRAMES timeframe,
   const int shift=0)
{
   CSessionContext context;

   context.Symbol      = symbol;
   context.Timeframe   = timeframe;
   const datetime barOpen=iTime(symbol,timeframe,shift);
   datetime observationTime=0;
   context.CurrentTime = (m_observation_time.Resolve(
                             barOpen,timeframe,observationTime) ?
                          observationTime : TimeCurrent());

   return context;
}

     
};

#endif
