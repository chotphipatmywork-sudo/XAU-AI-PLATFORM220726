//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalBrainReplay.mqh                              |
//| Layer   : Core / Brain                                           |
//| Version : 1.0.1                                                  |
//| Purpose : Replay Brain analysis at a historical bar              |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_HISTORICALBRAINREPLAY_MQH
#define CORE_BRAIN_HISTORICALBRAINREPLAY_MQH

#include "../data/DataManager.mqh"
#include "TrendAnalyzer.mqh"
#include "VolatilityAnalyzer.mqh"
#include "LiquidityAnalyzer.mqh"
#include "SessionAnalyzer.mqh"
#include "ClosedBarObservationTime.mqh"
#include "models/BrainAnalysisResult.mqh"

class CHistoricalBrainReplay
  {
private:
   CDataManager         m_data;
   CTrendAnalyzer       m_trend;
   CVolatilityAnalyzer  m_volatility;
   CLiquidityAnalyzer   m_liquidity;
   CSessionAnalyzer     m_session;
   CClosedBarObservationTime m_observation_time;

public:
   CBrainAnalysisResult Analyze(const string symbol,const ENUM_TIMEFRAMES timeframe,const int shift)
     {
      CBrainAnalysisResult result;
      if(symbol=="" || shift<0)
         return(result);

      const datetime bar_time=iTime(symbol,timeframe,shift);
      const double close=m_data.GetClose(symbol,timeframe,shift);
      if(bar_time<=0 || close<=0.0)
         return(result);

      datetime observation_time=0;
      if(!m_observation_time.Resolve(bar_time,timeframe,observation_time))
         return(result);

      CTrendContext trend_context;
      trend_context.Symbol=symbol;
      trend_context.Timeframe=timeframe;
      trend_context.Bars=m_data.Bars(symbol,timeframe)-shift;
      trend_context.Shift=shift;
      trend_context.Open=m_data.GetOpen(symbol,timeframe,shift);
      trend_context.High=m_data.GetHigh(symbol,timeframe,shift);
      trend_context.Low=m_data.GetLow(symbol,timeframe,shift);
      trend_context.Close=close;
      trend_context.Volume=(double)iVolume(symbol,timeframe,shift);

      CVolatilityContext volatility_context;
      volatility_context.Symbol=symbol;
      volatility_context.Timeframe=timeframe;
      volatility_context.Bars=trend_context.Bars;
      volatility_context.Shift=shift;

      CLiquidityContext liquidity_context;
      liquidity_context.Symbol=symbol;
      liquidity_context.Timeframe=timeframe;
      liquidity_context.Bars=trend_context.Bars;
      liquidity_context.Shift=shift;
      liquidity_context.High=trend_context.High;
      liquidity_context.Low=trend_context.Low;
      liquidity_context.Close=close;
      liquidity_context.Volume=trend_context.Volume;
      double volume_sum=0.0;
      liquidity_context.ReferenceHigh=m_data.GetHigh(symbol,timeframe,shift+1);
      liquidity_context.ReferenceLow=m_data.GetLow(symbol,timeframe,shift+1);
      for(int reference_shift=shift+1; reference_shift<=shift+10; reference_shift++)
        {
         const double high=m_data.GetHigh(symbol,timeframe,reference_shift);
         const double low=m_data.GetLow(symbol,timeframe,reference_shift);
         if(high>liquidity_context.ReferenceHigh)
            liquidity_context.ReferenceHigh=high;
         if(liquidity_context.ReferenceLow==0.0 || low<liquidity_context.ReferenceLow)
            liquidity_context.ReferenceLow=low;
         volume_sum+=(double)m_data.GetVolume(symbol,timeframe,reference_shift);
        }
      liquidity_context.AverageVolume=volume_sum/10.0;

      CSessionContext session_context;
      session_context.Symbol=symbol;
      session_context.Timeframe=timeframe;
      session_context.CurrentTime=observation_time;

      result.Trend=m_trend.Analyze(trend_context);
      result.Volatility=m_volatility.Analyze(volatility_context);
      result.Liquidity=m_liquidity.Analyze(liquidity_context);
      result.Session=m_session.Analyze(session_context);
      result.Valid=true;
      return(result);
     }
  };

#endif
