//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestAITrendScore.mq5                                   |
//| Layer   : Tests / Brain / Trend                                  |
//| Version : 2.0.0                                                  |
//| Purpose : Feature Contract 3.0 Trend component smoke test        |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/trend/assembler/TrendAssembler.mqh"

int OnInit()
  {
   CEMAResult ema;
   ema.FastEMA=102.0;
   ema.SlowEMA=100.0;
   ema.Bullish=true;
   CSlopeResult slope;
   slope.Value=0.20;
   slope.Rising=true;
   CStructureResult structure;
   structure.ValidStructure=true;
   CBOSResult bos;
   bos.ValidBreak=true;
   CCHOCHResult choch;
   CTrendAssembler assembler;
   const CTrendResult trend=assembler.Assemble(ema,slope,structure,bos,choch,1.0,98.0);
   const bool valid=(MathAbs(trend.Strength-100.0)<0.000001 &&
                     MathAbs(trend.AITrendScore-98.5)<0.000001 &&
                     MathAbs(trend.AITrendRegime-100.0)<0.000001 &&
                     MathAbs(trend.AITrendMomentum-100.0)<0.000001 &&
                     MathAbs(trend.AITrendSlope-90.0)<0.000001);
   Print("Trend runtime strength / AI trend score: ",trend.Strength,"/",trend.AITrendScore);
   Print("Trend AI components REGIME/MOMENTUM/SLOPE: ",
         trend.AITrendRegime,"/",trend.AITrendMomentum,"/",trend.AITrendSlope);
   Print("AI trend component contract valid: ",valid);
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
