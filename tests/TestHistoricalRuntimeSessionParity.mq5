//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalRuntimeSessionParity.mq5                 |
//| Layer   : Tests / Brain / Session                                |
//| Version : 1.0.0                                                  |
//| Purpose : Verify historical and runtime closed-bar Session parity |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/ClosedBarObservationTime.mqh"
#include "../core/brain/session/engines/SessionEngine.mqh"

bool CheckSessionCase(const string bar_open_value,
                      const string expected_observation_value,
                      const ENUM_SESSION_STATE expected_state,
                      const double expected_progress,
                      bool &timestamp_valid,
                      bool &state_valid,
                      bool &progress_valid)
  {
   CClosedBarObservationTime resolver;
   const datetime bar_open=StringToTime(bar_open_value);
   datetime historical_observation=0;
   const bool resolved=resolver.Resolve(
      bar_open,PERIOD_M15,historical_observation);
   const datetime runtime_observation=
      bar_open+PeriodSeconds(PERIOD_M15);
   const datetime expected_observation=
      StringToTime(expected_observation_value);

   CSessionContext historical_context;
   historical_context.Symbol=_Symbol;
   historical_context.Timeframe=PERIOD_M15;
   historical_context.CurrentTime=historical_observation;

   CSessionContext runtime_context;
   runtime_context.Symbol=_Symbol;
   runtime_context.Timeframe=PERIOD_M15;
   runtime_context.CurrentTime=runtime_observation;

   CSessionEngine engine;
   const CSessionResult historical=engine.Analyze(historical_context);
   const CSessionResult runtime=engine.Analyze(runtime_context);

   timestamp_valid=(timestamp_valid && resolved &&
                    historical_observation==runtime_observation &&
                    historical_observation==expected_observation);
   state_valid=(state_valid && historical.State==runtime.State &&
                historical.State==expected_state);
   progress_valid=(progress_valid &&
                   MathAbs(historical.Progress-runtime.Progress)<0.000001 &&
                   MathAbs(historical.Progress-expected_progress)<0.000001);
   return(timestamp_valid && state_valid && progress_valid);
  }

int OnInit()
  {
   bool timestamp_valid=true;
   bool state_valid=true;
   bool progress_valid=true;

   CheckSessionCase("2026.07.17 07:45","2026.07.17 08:00",
                    SESSION_LONDON,0.0,
                    timestamp_valid,state_valid,progress_valid);
   CheckSessionCase("2026.07.17 15:45","2026.07.17 16:00",
                    SESSION_NEWYORK,0.0,
                    timestamp_valid,state_valid,progress_valid);
   CheckSessionCase("2026.07.17 23:45","2026.07.18 00:00",
                    SESSION_ASIA,0.0,
                    timestamp_valid,state_valid,progress_valid);
   CheckSessionCase("2026.07.17 03:45","2026.07.17 04:00",
                    SESSION_ASIA,50.0,
                    timestamp_valid,state_valid,progress_valid);

   CClosedBarObservationTime resolver;
   datetime invalid_observation=1;
   const bool invalid_rejected=
      !resolver.Resolve(0,PERIOD_M15,invalid_observation) &&
      invalid_observation==0;
   const bool valid=(timestamp_valid && state_valid &&
                     progress_valid && invalid_rejected);

   Print("Historical/runtime observation timestamp parity valid: ",
         timestamp_valid);
   Print("Historical/runtime Session boundary parity valid: ",
         state_valid);
   Print("Historical/runtime Session progress parity valid: ",
         progress_valid);
   Print("Historical/runtime Session parity contract valid: ",valid);
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
