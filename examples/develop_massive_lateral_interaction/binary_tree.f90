module btree

    implicit none
    type ::  binary_tree
        real, allocatable, dimension(:) :: tdata
        integer :: levels, total_length, filled
    end type


contains

    function btree_init(n) result(self)
        type(binary_tree) :: self
        integer, intent(in) :: n


        self%levels = ceiling(log(real(n)) / log(2.) + 1)
        self%total_length = 2 ** self%levels
        allocate(self%tdata(self%total_length))
        self%filled = 0

    end function btree_init


    subroutine btree_destroy(self)
        type(binary_tree),  intent(inout) :: self

        deallocate(self%tdata)

    end subroutine btree_destroy


    subroutine btree_repr(self)
        type(binary_tree)  :: self
        integer :: a, b, n

        do n = 0, (self%levels - 1)
        a = 2 ** n
        b = 2 ** (n + 1) - 1
        enddo

    end subroutine btree_repr


    subroutine btree_add(self, value)
        type(binary_tree) :: self
        real :: value

        integer :: pos

        if(self%filled * 2 > self%total_length)then
            print *, "Tree is already full"
            stop
        endif

        pos = self%total_length / 2 + self%filled
        self%tdata(pos) = value
        call btree_update(self, pos)
        self%filled = self%filled + 1

    end subroutine btree_add


    subroutine btree_del(self, pos)
        type(binary_tree) :: self
        integer, intent(in) :: pos

        ! move deleted new data field
        self%tdata(pos) = self%tdata(self%filled)
        self%tdata(self%filled) = 0.

        ! update tree structure
        call btree_update(self, pos)
        call btree_update(self, self%filled)

        ! decrease tree structure
        self%filled = self%filled - 1

    end subroutine btree_del


    subroutine btree_replace(self, pos, new_rate)
        type(binary_tree) :: self
        real, intent(in) :: new_rate
        integer, intent(in) :: pos

        self%tdata(pos) = new_rate
        call btree_update(self, pos)

    end subroutine btree_replace


    subroutine btree_update(self, pos)
        type(binary_tree) :: self
        integer, intent(in) :: pos
        integer :: pos_

        pos_ = pos
        do while (pos_ > 1)
        pos_ = pos_ / 2
        self%tdata(pos_) = self%tdata(2 * pos_) + self%tdata(2 * pos_ + 1)

        end do
    end subroutine btree_update


    subroutine btree_pick(self, x, n)
        type(binary_tree), intent(in) :: self
        real, intent(inout) :: x
        integer, intent(out) :: n


        n = 1
        do while (n < self%total_length / 2)
        if (x < self%tdata(n)) then
            n = 2 * n
        else
            x = x - self%tdata(n)
            n = 2 * n + 2
        endif
        enddo

        if(x > self%tdata(n))then
            n = n + 1
        endif

        n = 1 + n - self%total_length / 2

    end subroutine btree_pick

end module btree

program main
    use btree
    implicit none


    type(binary_tree), dimension(:), allocatable :: t
    !type(binary_tree) :: t
    integer :: n, i, a
    real :: x, y, z


    n = 1

    allocate(t(n))
    do i =  1, n
    t(i) = btree_init(80)
    enddo

    do i = 1, 80
    call btree_add(t(1), 1.)
    enddo
    call btree_repr(t(1))


    do i = 1, n 
    call btree_destroy(t(i))
    enddo

end program
