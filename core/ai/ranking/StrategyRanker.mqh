//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : StrategyRanker.mqh                                     |
//| Layer   : Core / AI / Ranking                                   |
//| Version : 1.0.0                                                  |
//| Purpose : AI Strategy Ranking Foundation                         |
//+------------------------------------------------------------------+

#ifndef CORE_AI_RANKING_STRATEGYRANKER_MQH
#define CORE_AI_RANKING_STRATEGYRANKER_MQH


//--------------------------------------------------
// Strategy Rank Result
//--------------------------------------------------

class CStrategyRankResult
{

public:

   string StrategyName;

   double Score;

   bool Selected;


public:

   CStrategyRankResult()
   {
      Reset();
   }


   //--------------------------------------------------

   void Reset()
   {

      StrategyName = "";

      Score = 0.0;

      Selected = false;

   }

};


//--------------------------------------------------
// Strategy Ranker
//--------------------------------------------------

class CStrategyRanker
{

private:

   bool m_initialized;



public:


   //--------------------------------------------------

   CStrategyRanker()
   {
      m_initialized = false;
   }



   //--------------------------------------------------

   bool Initialize()
   {

      m_initialized = true;

      return true;

   }



   //--------------------------------------------------

   bool IsReady() const
   {
      return m_initialized;
   }



   //--------------------------------------------------
   // Evaluate Strategy
   //--------------------------------------------------

   CStrategyRankResult Evaluate(
      const string strategyName,
      const double performanceScore)
   {

      CStrategyRankResult result;


      if(!m_initialized)
         return result;


      result.StrategyName =
         strategyName;


      result.Score =
         performanceScore;


      result.Selected =
         (performanceScore > 0.0);


      return result;

   }



   //--------------------------------------------------

   void Shutdown()
   {

      m_initialized = false;

   }


};


#endif

//+------------------------------------------------------------------+