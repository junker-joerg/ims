if __name__ == "__main__":
    import multiprocessing

    # Frozen spawn workers must enter multiprocessing before desktop argument
    # parsing or window initialization, rather than starting another Workbench.
    multiprocessing.freeze_support()

    from ims.desktop.launcher import main

    raise SystemExit(main())
