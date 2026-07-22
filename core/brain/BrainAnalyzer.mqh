//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainAnalyzer.mqh                                      |
//| Layer   : Brain                                                  |
//| Version : 4.2.0                                                  |
//| Purpose : Market Analysis Coordinator                             |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_BRAINANALYZER_MQH
#define CORE_BRAIN_BRAINANALYZER_MQH


#include "BrainContextBuilder.mqh"

#include "TrendAnalyzer.mqh"
#include "VolatilityAnalyzer.mqh"
#include "LiquidityAnalyzer.mqh"
#include "SessionAnalyzer.mqh"

#include "models/BrainAnalysisResult.mqh"


//--------------------------------------------------
// Brain Analyzer
//--------------------------------------------------

class CBrainAnalyzer
{

private:


   CBrainContextBuilder m_builder;


   CTrendAnalyzer m_trend;


   CVolatilityAnalyzer m_volatility;


   CLiquidityAnalyzer m_liquidity;


   CSessionAnalyzer m_session;



public:


   //--------------------------------------------------

   CBrainAnalysisResult Analyze(
      const string symbol,
      ENUM_TIMEFRAMES timeframe,
      const int shift=0)
   {

      CBrainAnalysisResult result;



      //--------------------------------------------------
      // Trend
      //--------------------------------------------------

      CTrendContext trendContext =
         m_builder.BuildTrendContext(
            symbol,
            timeframe,
            shift);


      result.Trend =
         m_trend.Analyze(
            trendContext);



      //--------------------------------------------------
      // Volatility
      //--------------------------------------------------

      CVolatilityContext volatilityContext =
         m_builder.BuildVolatilityContext(
            symbol,
            timeframe,
            shift);


      result.Volatility =
         m_volatility.Analyze(
            volatilityContext);



      //--------------------------------------------------
      // Liquidity
      //--------------------------------------------------

      CLiquidityContext liquidityContext =
         m_builder.BuildLiquidityContext(
            symbol,
            timeframe,
            shift);


      result.Liquidity =
         m_liquidity.Analyze(
            liquidityContext);



      //--------------------------------------------------
      // Session
      //--------------------------------------------------

      CSessionContext sessionContext =
         m_builder.BuildSessionContext(
            symbol,
            timeframe,
            shift);


      result.Session =
         m_session.Analyze(
            sessionContext);



      //--------------------------------------------------

      result.Valid = true;


      return result;

   }

};


#endif

//+------------------------------------------------------------------+
