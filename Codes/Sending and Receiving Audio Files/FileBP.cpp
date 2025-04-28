#include "FileBP.h"
#include "Misc/Paths.h"
#include "HAL/PlatformProcess.h"
#include "Logging/LogMacros.h"

bool UFileBP::RunExternalFile(
    const FString& FilePath,
    const FString& Parameters,
    bool bLaunchDetached,
    bool bLaunchHidden,
    bool bLaunchReallyHidden
)
{
    UE_LOG(LogTemp, Warning, TEXT("RunExternalFile Called with: %s"), *FilePath);

    if (!FPaths::FileExists(FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("File does not exist: %s"), *FilePath);
        return false;
    }

    FString WorkingDirectory = FPaths::GetPath(FilePath);
    void* ReadPipe = nullptr;
    void* WritePipe = nullptr;

    FProcHandle ProcessHandle = FPlatformProcess::CreateProc(
        *FilePath,
        *Parameters,
        bLaunchDetached,
        bLaunchHidden,
        bLaunchReallyHidden,
        nullptr,
        0,
        *WorkingDirectory,
        ReadPipe,
        WritePipe
    );

    if (!ProcessHandle.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to launch external file: %s"), *FilePath);
        return false;
    }

    UE_LOG(LogTemp, Warning, TEXT("Successfully launched external file: %s"), *FilePath);
    return true;
}
