//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestSessionFeatureProgress.mq5                          |
//| Layer   : Tests / Brain / Session                                 |
//| Version : 1.0.0                                                   |
//| Purpose : Validate Session state and intra-session progress       |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/session/engines/SessionEngine.mqh"

bool CheckProgress(const string value,const ENUM_SESSION_STATE expected_state,
                   const double expected_progress)
  {
   CSessionEngine engine;
   CSessionContext context;
   context.Symbol=_Symbol;
   context.Timeframe=PERIOD_M15;
   context.CurrentTime=StringToTime(value);
   CSessionResult result=engine.Analyze(context);
   return(result.State==expected_state &&
          MathAbs(result.Progress-expected_progress)<0.000001);
  }

int OnInit()
  {
   const bool valid=(
      CheckProgress("2026.07.15 00:00",SESSION_ASIA,0.0) &&
      CheckProgress("2026.07.15 04:00",SESSION_ASIA,50.0) &&
      CheckProgress("2026.07.15 07:45",SESSION_ASIA,96.875) &&
      CheckProgress("2026.07.15 08:00",SESSION_LONDON,0.0) &&
      CheckProgress("2026.07.15 12:00",SESSION_LONDON,50.0) &&
      CheckProgress("2026.07.15 16:00",SESSION_NEWYORK,0.0) &&
      CheckProgress("2026.07.15 20:00",SESSION_NEWYORK,50.0) &&
      CheckProgress("2026.07.15 23:45",SESSION_NEWYORK,96.875));
   Print("Session feature progress valid: ",valid);
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
