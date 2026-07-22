//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionWorkspace.mqh                                 |
//| Layer   : Execution                                              |
//| Version : 1.0.0                                                  |
//| Purpose : Execution Workspace                                    |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_EXECUTIONWORKSPACE_MQH
#define CORE_EXECUTION_EXECUTIONWORKSPACE_MQH

#include "ExecutionContext.mqh"
#include "ExecutionResult.mqh"

//--------------------------------------------------
// Execution Workspace
//--------------------------------------------------

class CExecutionWorkspace
{
public:
    CExecutionContext Context;

    CExecutionResult Result;

public:
    CExecutionWorkspace()
    {
        Reset();
    }

    void Reset()
    {
        Context.Reset();
        Result.Reset();
    }
};

#endif