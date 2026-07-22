//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainAnalysisResult.mqh                                |
//| Layer   : Brain / Models                                         |
//| Version : 1.1.0                                                  |
//| Purpose : Final Brain Analysis Result                            |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_MODELS_BRAINANALYSISRESULT_MQH
#define CORE_BRAIN_MODELS_BRAINANALYSISRESULT_MQH


#include "../trend/models/TrendResult.mqh"

#include "../volatility/models/VolatilityResult.mqh"

#include "../liquidity/models/LiquidityResult.mqh"

#include "../session/models/SessionResult.mqh"


//--------------------------------------------------
// Brain Analysis Result
//--------------------------------------------------

class CBrainAnalysisResult
{

public:


   bool Valid;


   //--------------------------------------------------
   // Market Analysis
   //--------------------------------------------------

   CTrendResult Trend;


   CVolatilityResult Volatility;


   CLiquidityResult Liquidity;


   CSessionResult Session;



public:


   //--------------------------------------------------

   CBrainAnalysisResult()
   {
      Reset();
   }



   //--------------------------------------------------

   void Reset()
   {

      Valid = false;


      Trend.Reset();


      Volatility.Reset();


      Liquidity.Reset();


      Session.Reset();

   }

};


#endif

//+------------------------------------------------------------------+