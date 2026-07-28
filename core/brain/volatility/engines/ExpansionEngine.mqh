//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExpansionEngine.mqh                                    |
//| Layer   : Brain / Volatility / Engines                           |
//| Version : 1.0.0                                                  |
//| Purpose : Volatility Expansion Score Engine                      |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_ENGINES_EXPANSIONENGINE_MQH
#define CORE_BRAIN_VOLATILITY_ENGINES_EXPANSIONENGINE_MQH

class CExpansionEngine
{
public:
   double Analyze(const double ratio)
   {
      if(ratio<=1.0)
         return 0.0;
      return MathMax(0.0,MathMin(100.0,(ratio-1.0)*100.0));
   }
};

#endif
